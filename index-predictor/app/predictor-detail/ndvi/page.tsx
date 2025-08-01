import Image from 'next/image';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImages, faFileCsv, faMapLocation, faLocationDot, faSquare } from '@fortawesome/free-solid-svg-icons';

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

  return (
    <div className="px-5 py-3">
      <h4>ดัชนีความแตกต่างของพืช</h4>
      <div className="card d-flex flex-column mt-3" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <div className='d-flex flex-row justify-content-between'>
            <p>สัปดาห์ที่ทำนาย : week 45, 2025 (07/11/2025 - 13/11/2025)</p>
            <p>วันที่ดูข้อมูล : 04/07/2025 (สัปดาห์ที่ 27)</p>
          </div>
          <div className='d-flex flex-row py-3'>
            <div className='d-flex justify-content-start flex-column card-color ms-auto '>
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
          <div className='d-flex justify-content-center gap-3'>
            <button type="button" className="btn btn-info">
              <FontAwesomeIcon className='pe-2' icon="map-location" size="lg"></FontAwesomeIcon>
              Map view
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
      <div className="card d-flex flex-column mt-3" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <div className='d-flex flex-row'>
            <FontAwesomeIcon className='pe-2' icon="location-dot" size="lg"></FontAwesomeIcon>
            <p>ข้อมูลดัชนี NDVI ที่พิกัด 207, 270 </p>
          </div>
          <div className='d-flex flex-row'>
            <div>
              <p>กราฟ</p>
            </div>
            <div className='card card-index-detail ms-auto p-3'>
              <p>ค่า NDVI จากดาวเทียม</p>
              <p>ค่า NDVI จากการทำนาย</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}