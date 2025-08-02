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

const options: ChartOptions<'line'> = {
  responsive: true,
  plugins: {
    legend: { position: 'top' },
    title: { display: true, text: 'NDVI data for the previous 8 weeks', font: {size: 18} }
  }
};

const labels = [
  '2025-week13', '2025-week14', '2025-week15', '2025-week16',
  '2025-week17', '2025-week18', '2025-week19', '2025-week20', '2025-week45'
];

const data: ChartData<'line'> = {
  labels: labels,
  datasets: [
    {
        label: 'NDVI',
        data: [0.63, 0.35, 0.42, 0.58, 0.65, 0.72, 0.78, 0.85, 0.71],
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

const MyChart = () => {
  return <Line data={data} options={options} />;
};

export default MyChart;