import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import './list.css';
import { useState, useEffect } from 'react';

function NestedAccordion() {
    const [data, setData] = useState({});
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch('http://localhost:5000/api/medication-history')
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((json) => {
                console.log('Received data:', json);
                if (typeof json === 'object' && json !== null) {
                    setData(json);
                } else {
                    console.error('Invalid data format received:', json);
                    setError('Invalid data format received from server');
                }
            })
            .catch((error) => {
                console.error('Error fetching medication history:', error);
                setError(error.message);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <Typography>Loading medication history...</Typography>;
    }

    if (error) {
        return <Typography color="error">Error: {error}</Typography>;
    }

    if (!data || Object.keys(data).length === 0) {
        return <Typography>No medication history available</Typography>;
    }

    return (
        <div className="medication-list-container">
            {Object.entries(data).map(([medicineId, medData]) => (
                <Accordion key={medicineId}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <div className="mui-accordion-summary" style={{ width: '100%' }}>
                            <Typography className="medicine-header" style={{ flex: 1 }}>{medData.atc_code}</Typography>
                            <Typography className="atc-info" style={{ flex: 1 }}>{medData.atc_display}</Typography>
                            <Typography className="atc-info" style={{ flex: 1 }}>Continuums: {Object.keys(medData.medicine_id_part).length}</Typography>
                        </div>
                    </AccordionSummary>
                    <AccordionDetails>
                        {Object.entries(medData.medicine_id_part).map(([partId, partData]) => (
                            <Accordion key={partId}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography className="atc-info" style={{ flex: 1 }}> {partData.medication_requests[0].product} {partData.medication_requests[0].strength} {partData.medication_requests[0].form}</Typography>
                                    <Typography className="atc-info" style={{ flex: 1 }}>authored on: {partData.medication_requests[0].authored_on}</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    {partData.medication_requests.map((req, idx) => (
                                        <Typography className="atc-info">
                                            <pre>{JSON.stringify(req, null, 2)}</pre>
                                        </Typography>
                                    ))}
                                </AccordionDetails>
                            </Accordion>
                        ))}
                    </AccordionDetails>
                </Accordion>
            ))}
        </div>
    );
}

export default NestedAccordion;