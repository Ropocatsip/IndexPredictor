'use client';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface IndexData {
  week: string;
  data: number;
}

interface NdviDocument {
  _id: string;
  xAxis: number;
  yAxis: number;
  indexData: IndexData[];
}

type MyChartProps = {
  type: string;
  ndviDocument: NdviDocument | null;
};

const MyChart = ({ type, ndviDocument }: MyChartProps) => {
  const options: ChartOptions<'line'> = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: `${type} data for the previous 8 weeks`, font: {size: 18} }
    }
  };
  
  const labels = [] as string[];
  const datas = [] as number[];

  ndviDocument?.indexData.forEach(index => {
    labels.push(index.week);
    datas.push(index.data);
  });
  
  const data: ChartData<'line'> = {
    labels: labels,
    datasets: [
      {
          hidden: false,
          label: type,
          data: datas,
          backgroundColor: '#60a5fa',
          borderColor: '#60a5fa',
          pointBackgroundColor: labels.map((_, i) =>
              i === labels.length - 1 ? '#f97316' : '#60a5fa'
          ),
          pointBorderColor: labels.map((_, i) =>
              i === labels.length - 1 ? '#f97316' : '#60a5fa'
          ),
          pointRadius: 5,
          pointHoverRadius: 6,
          segment: {
              borderColor: (ctx) => {
                  const index = ctx.p0DataIndex;
                  return index === labels.length - 2 ? '#f97316' : '#60a5fa'; 
              }
          }
      }
    ]
  };

  return <Line data={data} options={options} />;
};

export default MyChart;