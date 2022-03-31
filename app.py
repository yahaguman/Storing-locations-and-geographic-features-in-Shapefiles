import os
from zipfile import ZipFile

from flask import Flask, request, flash, redirect
from werkzeug.utils import secure_filename

from flask_restful import Resource, Api
import shapefile

UPLOAD_FOLDER = 'uploads/shapefile/'
ALLOWED_EXTENSIONS = {'zip'}


app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#unzip shapefile
def unzip_shapefile(shp):
    shape_files = []
    with ZipFile(shp) as zipObj:
        zipObj.extractall('media/shapefile/')
        list_files = zipObj.namelist()
        for elem in list_files:
            shape_files.append(elem)
    shape_file = shape_files[0]
    file_name = os.path.splitext(shape_file)[0]
    file_path = 'media/shapefile/' + file_name + '.shp'
    return file_path


class CreatePoint(Resource):
    def post(self):
        point_a_lat = request.json.get('point_a_lat')
        point_a_lon = request.json.get('point_b_lon')

        shp = shapefile.Writer('point')
        shp.field('name', 'C')
        shp.point(point_a_lat, point_a_lon)
        shp.record('point1')
        shp.close()

        return 'done'


class CreateLine(Resource):

    def post(self):
        point_a_lat = request.json.get('point_a_lat')
        point_a_lon = request.json.get('point_a_lon')
        point_b_lat = request.json.get('point_b_lat')
        point_b_lon = request.json.get('point_b_lon')

        shp = shapefile.Writer('line')
        shp.field('name', 'C')
        shp.field('School', 'C', size=250)
        shp.line([[[point_a_lat, point_a_lon], [point_b_lat, point_b_lon]]])
        shp.record('peter', 'Boy went to school')
        shp.close()

        return 'done'


class CreatePolygon(Resource):

    def post(self):
        point_a_lat = request.json.get('point_a_lat')
        point_a_lon = request.json.get('point_a_lon')
        point_b_lat = request.json.get('point_b_lat')
        point_b_lon = request.json.get('point_b_lon')
        point_c_lat = request.json.get('point_c_lat')
        point_c_lon = request.json.get('point_c_lon')
        point_d_lat = request.json.get('point_d_lat')
        point_d_lon = request.json.get('point_d_lon')

        shp = shapefile.Writer('poly')
        shp.field('name', 'C')
        shp.poly([
            [[point_a_lat,point_a_lon], [point_b_lat,point_b_lon], [point_c_lat,point_c_lon],
             [point_d_lat,point_d_lon], [point_a_lat,point_a_lon]]

             ])
        shp.record('polygon')
        shp.close()

        return 'done'


class ReadShapefile(Resource):

    def post(self):
        file = request.files['file']
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with shapefile.Reader(unzip_shapefile(file)) as shp:
            print(shp.bbox)
            print(shp.records())
            print(len(shp))
        return 'done'


api.add_resource(CreatePoint, '/api/point')
api.add_resource(CreateLine, '/api/line')
api.add_resource(CreatePolygon, '/api/polygon')
api.add_resource(ReadShapefile, '/api/read')


if __name__ == '__main__':
    app.run(debug=True)

