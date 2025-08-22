"use client";
import { useEffect, useState } from "react";
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImages, faFileCsv, faMapLocation, faLocationDot, faSquare } from '@fortawesome/free-solid-svg-icons';
import MyChart from '../components/my-chart';
import { getISOWeek, startOfISOWeek, addWeeks, format } from 'date-fns';
import { GoogleMapView } from '../components/google-map-view';
import { MapComponent } from '../components/map';
import Image from "next/image";

library.add(faImages, faFileCsv, faMapLocation, faLocationDot, faSquare);

export default function NDVI() {

  const colors = [
    { id: 1, title: '1.0', color: '#FF00BF' },
    { id: 2, title: '0.9', color: '#B600FF', desc: 'Highly density' },
    { id: 3, title: '0.8', color: '#2900FF' },
    { id: 4, title: '0.7', color: '#005EFF' },
    { id: 5, title: '0.6', color: '#00EBFF' },
    { id: 6, title: '0.5', color: '#00FF8B', desc: 'Moderately density' },
    { id: 7, title: '0.4', color: '#00FF00' },
    { id: 8, title: '0.3', color: '#8CFF00' },
    { id: 9, title: '0.2', color: '#FFEA00', desc: 'Slightly density' },
    { id: 10, title: '0.1', color: '#FF5D00' },
    { id: 11, title: '0.0', color: '#FF0028' },
    { id: 12, title: '-0.1', color: '#FF0028' },
    { id: 13, title: '-0.2', color: '#FF0028' },
    { id: 14, title: '-0.3', color: '#FF0028' },
    { id: 15, title: '-0.4', color: '#FF0028', desc: 'No vegtation' },
    { id: 16, title: '-0.5', color: '#FF0028' },
    { id: 17, title: '-0.6', color: '#FF0028' },
    { id: 18, title: '-0.7', color: '#FF0028' },
    { id: 19, title: '-0.8', color: '#FF0028' },
    { id: 20, title: '-0.9', color: '#FF0028' },
    { id: 21, title: '-1.0', color: '#FF0028' }
  ];

  
  const now = new Date();
  const jan4 = new Date(now.getFullYear(), 0, 4); // Jan 4 is always in the first ISO week
  const firstISOWeekStart = startOfISOWeek(jan4);
  const weekNumber = getPredictedWeekNumber(); 
  const startDate = addWeeks(firstISOWeekStart, weekNumber - 1);
  const predictedDateStart = format(startDate, 'dd/MM/yyyy');
  const predictedDateEnd = format(addWeeks(startDate, 1), 'dd/MM/yyyy');
  const [isMapView, setIsMapView] = useState(false);

  const toggleView = () => {
    setIsMapView((prev) => !prev); // toggle true/false
  };

  const [imageUrl, setImageUrl] = useState<string | null>(null);
  useEffect(() => {
    const fetchImage = async () => {
      const now = new Date();
      const weekNumber = 45; // replace with your calculation
      
      const res = await fetch(
        `http://127.0.0.1:5000/predict/ndvi/${now.getFullYear()}-week${weekNumber}`,
        {
          method: "GET",
          cache: "no-store",
        }
      );

      if (!res.ok) {
        console.error("Failed to fetch image");
        return;
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setImageUrl(url);
    };

    fetchImage();
  }, []);

  function getPredictedWeekNumber(): number {
    if (getISOWeek(now) <= 20 || getISOWeek(now) >= 45) return getISOWeek(now);
    else return 45;
  }

  return (
    <div className="px-5 py-3">
      <h4>ดัชนีความแตกต่างของพืช</h4>
      {/* Predicted Index */}
      <div className="card d-flex flex-column mt-3" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <div className='d-flex flex-row justify-content-between'>
            <p>สัปดาห์ที่ทำนาย : week {weekNumber}, {now.getFullYear()} ({predictedDateStart} - {predictedDateEnd})</p>
            <p>วันที่ดูข้อมูล : {now.toLocaleDateString('th-TH', { year: 'numeric', month: '2-digit', day: '2-digit' })} (สัปดาห์ที่ {getISOWeek(now)})</p>
          </div>
          {/* picture */}
          <div className='d-flex flex-row py-3 gap-3'>
            <div className='flex-grow-1'>
              {isMapView ? (
                <GoogleMapView>
                  <MapComponent />
                </GoogleMapView>
              ) : imageUrl ? (
                <div className="d-flex justify-content-center">
                  <Image
                    src={imageUrl}
                    alt="NDVI Prediction"
                    width={600}
                    height={500}     
                    className="border rounded"
                  />
                </div>
              ) : (
                <p>Loading image...</p>
              )}
            </div>
            <div className='d-flex ms-auto'>
              <div className='d-flex justify-content-start flex-column card-color'>
                {colors.map((color) => (
                  <div key={color.id}>
                    <div className='d-flex flex-row'>
                      <FontAwesomeIcon icon="square" size="lg" color={color.color}></FontAwesomeIcon>
                      {color.title}
                      <div className='d-flex ms-auto px-2'>
                        {color.desc}
                      </div>
                    </div>
                    {(color.id == 4 || color.id == 7 || color.id == 10) ? (<hr className='line'></hr>): ""}
                  </div>
                ))}
              </div>
            </div>
          </div>
          {/* button */}
          <div className='d-flex justify-content-center gap-5'>
            <button type="button" className="btn btn-info" onClick={toggleView}>
              <FontAwesomeIcon className="pe-2" icon="map-location" size="lg" />
              {isMapView ? "Map view" : "Predictor view"}
            </button>
            <button type="button" className="btn btn-success">
              <FontAwesomeIcon className='pe-2' icon="file-csv" size="lg"></FontAwesomeIcon>
              Save as csv.
            </button>
            <button type="button" className="btn btn-primary">
              <FontAwesomeIcon className='pe-2' icon="images" size="lg"></FontAwesomeIcon>
              Download png.
            </button>
          </div>
        </div>
      </div>
      {/* Chart */}
      <div className="card d-flex flex-column mt-3" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <div className='d-flex flex-row'>
            <FontAwesomeIcon className='pe-2' icon="location-dot" size="lg"></FontAwesomeIcon>
            <p>ข้อมูลดัชนี NDVI ที่พิกัด 207, 270 </p>
          </div>
          <div className='d-flex flex-row'>
            <div className='flex-grow-1 flex-column  me-3'>
              <MyChart type="NDVI" />
            </div>
            <div className="d-flex flex-column legend-card">
              <div className="legend-item">
                  <div className="legend-symbol">
                      <div className="circle blue-color"></div>
                      <div className="line-icon blue-color"></div>
                  </div>
                  <span>ค่า NDVI จากดาวเทียม</span>
              </div>

              <div className="legend-item">
                  <div className="legend-symbol">
                      <div className="circle orange-color"></div>
                      <div className="line-icon orange-color"></div>
                  </div>
                  <span>ค่า NDVI จากการทำนาย</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}