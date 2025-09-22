import ee
import requests
import numpy
import io
import pandas as pd 
import datetime
from PIL import Image
from matplotlib import cm
import rasterio

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

def normalize(band):
    band_min, band_max = (band.min(), band.max())
    return ((band-band_min)/((band_max - band_min)))

def fetchAndSaveCsv(startDate, endDate):

    startDate = ee.Date.fromYMD(startDate.year, startDate.month, startDate.day)
    endDate = ee.Date.fromYMD(endDate.year, endDate.month, endDate.day)
    
    s2 = importFarmManagement(studyArea, startDate, endDate)
    try:
        collectionList = s2.toList(s2.size())
        collectionSize = collectionList.size().getInfo()
        print(f"There are {collectionSize} files.")

    except Exception as e:
        print("There are no new data.")
        print(e)
        return 0

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

def fetchAndSaveRasterCsv(startDate, endDate):

    startDate = ee.Date.fromYMD(startDate.year, startDate.month, startDate.day)
    endDate = ee.Date.fromYMD(endDate.year, endDate.month, endDate.day)
    
    s2 = importFarmManagement(studyArea, startDate, endDate)
    try:
        collectionList = s2.toList(s2.size())
        collectionSize = collectionList.size().getInfo()
        print(f"There are {collectionSize} files.")

    except Exception as e:
        print("There are no new data.")
        print(e)
        return 0

    last_index = collectionList.size().subtract(1)
    image = ee.Image(collectionList.get(last_index))

    imageRGB = image
    url = imageRGB.getDownloadUrl({
        'bands': ['B4', 'B3', 'B2'],
        'region': studyAreaRGB,
        'scale': 1,
        'format': 'GEO_TIFF'
    })
    response = requests.get(url)
    filenameTif = 'data/raster/latest_rgb.tif'
    with open(filenameTif, 'wb') as fd:
        fd.write(response.content)

    dataset = rasterio.open(filenameTif)
    img=dataset.read(1)
    red = dataset.read(1)
    green = dataset.read(2)
    blue = dataset.read(3)

    imgdataRed = numpy.array(red)
    imgdataGreen = numpy.array(green)
    imgdataBlue = numpy.array(blue)

    red_n = normalize(imgdataRed)
    green_n = normalize(imgdataGreen)
    blue_n = normalize(imgdataBlue)

    imgdata= numpy.dstack((red_n, green_n, blue_n))
    rgb = (numpy.dstack((red_n,green_n,blue_n)) * 255.999) .astype(numpy.uint8)

    img = Image.fromarray(rgb)
    img.save('data/raster/latest_rgb.jpeg')