import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const LABELS = {
  carbon_stock: 'Carbon stock',
  canopy_cover: 'Canopy cover',
  species_richness: 'Species richness',
};

export default function MetricChart({ metricKey, points }) {
  const unit = points[0]?.unit || '';

  const data = {
    labels: points.map((p) => p.date.slice(0, 4)),
    datasets: [
      {
        label: `${LABELS[metricKey] || metricKey} (${unit})`,
        data: points.map((p) => p.value),
        borderColor: '#1f6f4a',
        backgroundColor: 'rgba(31, 111, 74, 0.12)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { position: 'top' } },
    scales: { y: { beginAtZero: false, title: { display: true, text: unit } } },
  };

  return (
    <div className="chart-box">
      <Line data={data} options={options} />
    </div>
  );
}
