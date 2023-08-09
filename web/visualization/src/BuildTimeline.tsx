
// BuildTimeline.tsx
import React, { useState, useEffect } from 'react';
import Timeline from 'react-vis-timeline';
import './BuildTimeline.css';
export {};
interface DataItem {
  Date: string;
  OS: string;
  Arch: string;
  Release: string;
  Result: string;
}

const BuildTimeline: React.FC = () => {
  const [data, setData] = useState<DataItem[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<
    { start: Date; end: Date; title: string; content: string }[]
  >([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('month_tool_build_report.json'); // Update with the correct path
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (data.length > 0) {
      const events = data.map((item: DataItem) => ({
        start: new Date(item.Date),
        end: new Date(item.Date),
        title: `${item.OS} - ${item.Arch}`,
        content: item.Result === 'FAILED' ? 'Failed' : 'Passed',
      }));
      setTimelineEvents(events);
    }
  }, [data]);

  return (
    <section className="timeline-section">
      <h2>Build Timeline</h2>
      <Timeline
        items={timelineEvents}
        defaultTimeStart={new Date()}
        defaultTimeEnd={new Date()}
        stackItems
      />
    </section>
  );
};

export default BuildTimeline;
