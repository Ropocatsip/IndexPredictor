"use client";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useEffect, useState } from 'react';
import { faImages, faFileCsv, faMapLocation, faLocationDot, faSquare } from '@fortawesome/free-solid-svg-icons';
import { library } from '@fortawesome/fontawesome-svg-core';

library.add(faImages, faFileCsv, faMapLocation, faLocationDot, faSquare);

export default function COORDINATES() {
  const [loading, setLoading] = useState(true);
  interface IndexData {
    week: string;
    data: number;
  }

  interface NdviDocument {
    _id: string;
    xAxis: number;
    yAxis: number;
    indexData: IndexData[];
    top: number;
    left: number;
  }

    const [locations, setLocations] = useState<
      { x: number; y: number; }[]
    >([]);

  useEffect(() => {
      async function fetchAllNdvi() {
        try {
          setLoading(true); // reset loading before fetch
          const res = await fetch(`/api/index/ndvi`);
          if (!res.ok) {
            throw new Error("Failed to fetch");
          }
          const data: NdviDocument[] = await res.json();
          const mappedLocations = data.map((doc) => ({
            x: doc.xAxis,
            y: doc.yAxis
          }));
  
          setLocations(mappedLocations);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      }
      fetchAllNdvi();
    }, []);

    const addIndexCoordinates = () => {
      console.log("test");
      
    };

    const deleteIndexCoordinates = async (x: number, y: number) => {
      try {
        setLoading(true);
        const resndmi = await fetch(`/api/index/ndmi`,{
          method: "DELETE",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ row: x, column: y })
        });

        if (!resndmi.ok) {
          throw new Error("Failed to fetch");
        }

        const resndvi = await fetch(`/api/index/ndvi`,{
          method: "DELETE",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ row: x, column: y })
        });

        if (!resndvi.ok) {
          throw new Error("Failed to fetch");
        }

        setLocations(prev => prev.filter(item => !(item.x === x && item.y === y)));

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

  return (
    <div className="px-5 py-3">
      <h4>ตั้งค่าพิกัด</h4>
      {/* exist coordinates */}
      <div className="card d-flex flex-column mt-3" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <p>พิกัดเดิม</p>
          <table className="table">
            <thead>
              <tr>
                <th scope="col">ตำแหน่ง (row, column) ในไฟล์ Excel</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              {locations.map((u, index) => (
                <tr key={index}>
                  <td>({u.x}, {u.y})</td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-sm btn-danger"
                      onClick={() => deleteIndexCoordinates(u.x, u.y)}
                    >
                      <i className="bi bi-trash"></i> ลบ
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {/* new coordinates */}
      <div className="card d-flex flex-column mt-3 mb-5" style={{ width: '100%' }}>
        <div className="card-body d-flex flex-column px-5">
          <div className='d-flex flex-row'>
            <FontAwesomeIcon className='pe-2' icon="location-dot" size="lg"></FontAwesomeIcon>
            <p>พิกัดใหม่</p>
          </div>
          <div className='d-flex flex-row justify-content-between align-items-center'>
            <div className="container">
              <div className="row">
                <div className="col-sm">
                  <div className="input-group mb-3">
                    <span className="input-group-text" id="basic-addon1">column</span>
                    <input type="number" className="form-control" placeholder="column" aria-label="column" aria-describedby="basic-addon1"/>
                  </div>
                </div>
                <div className="col-sm">
                  <div className="input-group mb-3">
                    <span className="input-group-text" id="basic-addon1">row</span>
                    <input type="number" className="form-control" placeholder="row" aria-label="row" aria-describedby="basic-addon1"/>
                  </div>
                </div>
                <div className="col-sm align-items-end">
                  <button type="button" className="btn btn-success mb-3" onClick={addIndexCoordinates}>
                    เพิ่ม 
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}