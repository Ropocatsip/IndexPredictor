import Link from "next/link";
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFacebook, faLinkedin, faYoutube, faInstagram } from "@fortawesome/free-brands-svg-icons";

library.add(faFacebook, faLinkedin, faYoutube, faInstagram);

export default function Footer() 
{
    return (<>
        <footer className="footer text-muted px-5 py-5 position-absolute bottom-0 start-0 w-100">
            <hr />
            <p className="mb-4">IndexPredictor</p>
            <p>National Electronics and Computer Technology Center x Chulalongkorn University</p>
            <div className="d-flex">
                <Link className="icon-link  me-3" href="#">
                    <FontAwesomeIcon icon={['fab', 'facebook']} size="lg" color="#828282" />
                </Link>
                <Link className="icon-link  me-3" href="#" >
                    <FontAwesomeIcon icon={['fab', 'linkedin']} size="lg" color="#828282" />
                </Link>
                <Link className="icon-link  me-3" href="#" >
                    <FontAwesomeIcon icon={['fab', 'youtube']} size="lg" color="#828282" />
                </Link>
                <Link className="icon-link  me-3" href="#" >
                    <FontAwesomeIcon icon={['fab', 'instagram']} size="lg" color="#828282" />
                </Link>
            </div>
        </footer>
    </>);
}