import Image from 'next/image';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImages, faFileCsv, faMapLocation, faLocationDot } from '@fortawesome/free-solid-svg-icons';

library.add(faImages, faFileCsv, faMapLocation, faLocationDot);

export default function NDVI() {
  return (
    <div className="px-5 py-3">
      <h4>ดัชนีความแตกต่างของพืช</h4>
      <div className="card d-flex flex-column mt-3" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <div className='d-flex flex-row justify-content-between'>
            <p>สัปดาห์ที่ทำนาย : week 45, 2025 (07/11/2025 - 13/11/2025)</p>
            <p>วันที่ดูข้อมูล : 04/07/2025 (สัปดาห์ที่ 27)</p>
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