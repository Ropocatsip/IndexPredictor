'use client'

//Map component Component from library
import { GoogleMap } from "@react-google-maps/api";

//Map's styling
export const defaultMapContainerStyle = {
    width: '100%',
    height: '65vh',
    borderRadius: '5px',
};

const MapComponent = () => {
    const coords = [
        [101.5618,12.84945],
        [101.5618,12.8505],
        [101.5635,12.850],
        [101.5635,12.8492]
    ];
    const avgLng = coords.reduce((sum, c) => sum + c[0], 0) / coords.length;
    const avgLat = coords.reduce((sum, c) => sum + c[1], 0) / coords.length;

    const defaultMapCenter = {
        lat: avgLat,
        lng: avgLng
    }
    const defaultMapZoom = 18;
    const defaultMapOptions = {
        zoomControl: true,
        tilt: 0,
        gestureHandling: 'auto',
        mapTypeId: 'satellite',
    };

    return (
        <div>
            <GoogleMap 
                mapContainerStyle={defaultMapContainerStyle}
                center={defaultMapCenter}
                zoom={defaultMapZoom}
                options={defaultMapOptions}>
            </GoogleMap>
        </div>
    )
};

export { MapComponent };