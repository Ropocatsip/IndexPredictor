import Image from 'next/image';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLocationDot } from '@fortawesome/free-solid-svg-icons';
import Link from 'next/link';

library.add(faLocationDot);

export default function Home() {
  return (
    <div className="d-flex align-items-center p-5 justify-content-between">
      <Link href="/predictor-detail/ndvi" className="text-decoration-none text-reset">
        <div className="card d-flex flex-column" style={{ maxWidth: '350px', width: '100%' }}>
          <div style={{ position: 'relative', width: '100%', height: '200px' }}>
            <Image
              src="/land.png" // replace with your image path
              alt="Card Image"
              layout="fill"
              objectFit="cover"
              className="card-img-top"
            />
          </div>

          <div className="card-body d-flex flex-column">
            <div className='d-flex flex-row gap-2 py-2'>
              <FontAwesomeIcon icon="location-dot" size="lg" color='white'></FontAwesomeIcon>
              <h5 className="card-title cardtitle">สวนทุเรียนเวียงจันทร์</h5>
            </div>
            <div className='d-flex flex-row gap-3'>
              <FontAwesomeIcon icon="location-dot" size="lg" color='#54BBFE'></FontAwesomeIcon>
              <p className="card-text text-muted ">
                Rd Nong Kan Wang Chan,  Wang Chan District, Rayong 21210
              </p>
            </div>
          </div>
        </div>
      </Link>
    </div>
  );
}
