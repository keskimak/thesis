import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import './list.css';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { useState, useEffect } from 'react';

function NestedAccordion() {
    const [data, setData] = useState({});
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [aeExpanded, setAeExpanded] = useState(false);
    const [indicationsExpanded, setIndicationsExpanded] = useState(false);
    const [selectedValue, setSelectedValue] = useState("mau");
    const [selectedMedicineId, setSelectedMedicineId] = useState(null);
    const [selectedMedData, setSelectedMedData] = useState(null);
    const [openAd, setOpenAd] = useState(false);
    const [openId, setOpenId] = useState(false);

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
    const handleClickOpenAd = (medicineId, medData) => {
        setSelectedMedicineId(medicineId);
        setSelectedMedData(medData);
        setOpenAd(true);
    };

    const handleClickOpenId = (medicineId, medData) => {
        setSelectedMedicineId(medicineId);
        setSelectedMedData(medData);
        setOpenId(true);
    };

    const handleClose = () => {
        setOpenAd(false);
        setOpenId(false);
    };
    return (
        <div className="medication-list-container">
            <h1>Medication History</h1>

            {Object.entries(data).map(([medicineId, medData]) => (
                <Accordion key={medicineId}>
                    <AccordionSummary className="accordion-summary" expandIcon={<ExpandMoreIcon />}>
                        <div className="accordion-summary" style={{ width: '100%' }}>
                            <Typography className="atc-info" style={{ flex: 1 }}>{medData.atc_display} ({medData.atc_code})</Typography>
                            <Typography className="atc-info" style={{ flex: 1 }}>continuums: {Object.keys(medData.medicine_id_part).length}</Typography>
                            <br />
                            <Button variant="outlined" style={{ flex: 0.5 }} onClick={() => handleClickOpenAd(medicineId, medData)}>
                                ADVERSE EFFECTS
                            </Button>
                            <Button variant="outlined" style={{ flex: 0.5 }} onClick={() => handleClickOpenId(medicineId, medData)}>
                                INDICATIONS
                            </Button>

                        </div>
                    </AccordionSummary>
                    <AccordionDetails>
                        {Object.entries(medData.medicine_id_part).map(([partId, partData]) => (
                            <Accordion key={partId}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography className="atc-info" style={{ flex: 1 }}> {partData.medication_requests[0].product} {partData.medication_requests[0].strength} {partData.medication_requests[0].form}</Typography>
                                    <Typography className="atc-info" style={{ flex: 1 }}>authored on: {partData.medication_requests[0].authored_on}</Typography>
                                    <Typography className="atc-info" style={{ flex: 1 }}>MedicationRequests: {partData.medication_requests.length}</Typography>
                                    <Button variant="outlined" style={{ flex: 0.5 }} onClick={() => handleClickOpenAd(medicineId, partData)}>
                                        ADVERSE EFFECTS
                                    </Button>
                                    <Button variant="outlined" style={{ flex: 0.5 }} onClick={() => handleClickOpenId(medicineId, partData)}>
                                        INDICATIONS
                                    </Button>
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
                </Accordion >
            ))
            }
            <Dialog onClose={handleClose} open={openAd}>
                <DialogTitle>ADVERSE EFFECTS</DialogTitle>
                <List sx={{ pt: 0 }}>
                    {selectedMedData && Object.values(selectedMedData.medicine_id_part)
                        .flatMap(part =>
                            part.medication_requests.flatMap((req, reqIdx) =>
                                (req.adverse_effects || []).map((ae, aeIdx) => (
                                    <ListItem disablePadding key={`${req.id}-${aeIdx}`}>
                                        <ListItemText primary={`AE: ${ae.code}`} />
                                        <ListItemText primary={`Reported: ${req.authored_on}`} />
                                    </ListItem>

                                ))
                            )
                        )}
                </List>
            </Dialog>

            <Dialog onClose={handleClose} open={openId}>
                <DialogTitle>INDICATIONS</DialogTitle>
                <List sx={{ pt: 0 }}>
                    {selectedMedData && Object.values(selectedMedData.medicine_id_part)
                        .flatMap(part =>
                            part.medication_requests.flatMap((req, reqIdx) =>
                                (req.indications || []).map((ind, indIdx) => (
                                    <ListItem disablePadding key={`${req.id}-${indIdx}`}>
                                        <ListItemText primary={`Indication: ${ind.code}`} />
                                        <ListItemText primary={`Reported: ${req.authored_on}`} />
                                    </ListItem>

                                ))
                            )
                        )}
                </List>
            </Dialog>
        </div >

    );
}

export default NestedAccordion;