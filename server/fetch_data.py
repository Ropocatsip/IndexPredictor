import ee
import requests
import numpy
import io
import pandas as pd 
import datetime
from PIL import Image
from matplotlib import cm

service_account = 'opor-earthengine@master-project-nudthaya.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'master-project-nudthaya-b00cfbf908da.json')
ee.Initialize(credentials)

studyArea = ee.Geometry.Polygon(
    [[[101.5618,12.84945],
      [101.5618,12.8505],
      [101.5635,12.850],
      [101.5635,12.8492]]]); 

studyAreaRGB = ee.Geometry.Polygon(
    [[[101.5610,12.848],
      [101.5610,12.8515],
      [101.5645,12.851],
      [101.5645,12.848]]]); 

CloudCoverMax = 50

def getNDVI(image):
    ndvi = image.normalizedDifference(['B8','B4']).rename("NDVI")
    image = image.addBands(ndvi)
    return(image)

def addDate(image):
    img_date = ee.Date(image.date())
    img_date = ee.Number.parse(img_date.format('YYYYMMdd'))
    return image.addBands(ee.Image(img_date).rename('date').toInt())

def addNDMI(image):
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('ndmi')
    return image.addBands([ndmi])

def addNDWI(image):
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('ndwi')
    return image.addBands([ndwi])

def importFarmManagement(studyArea,startDate,endDate):
    
    # Get Sentinel-2 data
    s2s =(ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
          .filterDate(startDate,endDate)
          .filterBounds(studyArea)
          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',CloudCoverMax))
          .filter(ee.Filter.lt('CLOUD_COVERAGE_ASSESSMENT',CloudCoverMax))
          .map(getNDVI)
          .map(addDate)
          .map(addNDMI)
          .map(addNDWI))
    def scaleBands(img):
        prop = img.toDictionary()
        t = (img.select(['QA60','B2','B3','B4','B5','B6','B7','B8','B9','B11','B12','NDVI','ndmi','ndwi'])  
             .divide(1))
        t = (t.addBands(img.select(['QA60'])).set(prop)
            .copyProperties(img,['system:time_start','system:footprint']))
        return ee.Image(t)     
    s2s =s2s.map(scaleBands)
    
    return s2s
def canopy(studyArea) :
    canopy = (ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight").mosaic()
              .clip(studyArea))

    forest=canopy
    return forest

# def saveCanopy(): 
#     forestmask = canopy(studyArea).mask()#.clip(studyArea) 
#         #imageSen1VV = image 

#     forestmask = canopy(studyArea).mask()#.clip(studyArea) 
#     forest= canopy(studyArea)
#     forest =forest.And(forestmask)

#     url = forest.getDownloadUrl({
#             'bands': ['cover_code'],
#             'region': studyAreaRGB,
#             'scale': 1,
#             'format': 'NPY'
#     })
#     response = requests.get(url)
#     data = numpy.load(io.BytesIO(response.content))
#     # print(data)
#     # print(data.dtype)
#     # print(type(data))
#     # print(data.shape)
#     index = ['Row'+str(i) for i in range(1, len(data)+1)]
#     vv=data['cover_code']

#     vv_norm = (vv-numpy.min(vv))/(numpy.max(vv)-numpy.min(vv))  
#     # print("VV")
#     # print(vv)
#     im = Image.fromarray(numpy.uint8(cm.gist_rainbow(vv_norm)*255))
#     im.save("img/canopy.png")
#     # im.save("/var/www/html/Rayong02/image/canopy.png")

#     DF = pd.DataFrame(vv) 
#     # print(DF)

#         # save the dataframe as a csv file 
#     DF.to_csv("img/canopy.csv")

def fetchAndSaveCsv(startDate, endDate):

    startDate = ee.Date.fromYMD(startDate.year, startDate.month, startDate.day)
    endDate = ee.Date.fromYMD(endDate.year, endDate.month, endDate.day)
    
    s2 = importFarmManagement(studyArea, startDate, endDate)
    try:
        collectionList = s2.toList(s2.size())
        collectionSize = collectionList.size().getInfo()

        print(f"start fetching data from {startDate} to {endDate}")

    except Exception as e:
        print("There are no new data.")
        print(e)
        return []

    #  get raw data  
    for i in range(collectionSize):
        image = ee.Image(collectionList.get(i))

        epoch = image.get("system:time_start").getInfo()
        timestamp = datetime.datetime.fromtimestamp(epoch/1e3)
        timestring=timestamp.strftime('%Y-%m-%d')
        image_name = timestring

        imageNDVI = image.select(['NDVI']).clip(studyArea)    
        urlNDVI = imageNDVI.getDownloadUrl({
            'bands': ['NDVI'],
            'region': studyAreaRGB,
            'scale': 1,
            'format': 'NPY'
        })

        imageNDMI = image.select(['ndmi']).clip(studyArea)    
        urlNDMI = imageNDMI.getDownloadUrl({
            'bands': ['ndmi'],
            'region': studyAreaRGB,
            'scale': 1,
            'format': 'NPY'
        })

        responseNDVI = requests.get(urlNDVI)
        responseNDMI = requests.get(urlNDMI)
        dataNDVI = numpy.load(io.BytesIO(responseNDVI.content))
        dataNDMI = numpy.load(io.BytesIO(responseNDMI.content))

        ndvi=dataNDVI['NDVI']
        ndmi=dataNDMI['ndmi']

        DFNDVI = pd.DataFrame(ndvi)
        DFNDVI.to_csv('data/ndvi/rawdata/' + image_name + "_ndvi.csv")

        DFNDMI = pd.DataFrame(ndmi)
        DFNDMI.to_csv('data/ndmi/rawdata/' + image_name + "_ndmi.csv")

        print("ndvi and ndmi saved for " + timestring)