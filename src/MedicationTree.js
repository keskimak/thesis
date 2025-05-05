import React from 'react';
import {
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Typography,
    Box
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const MedicationTree = ({ data }) => {
    return (
        <Box sx={{ margin: 2 }}>
            {Object.entries(data).map(([medicineId, medData]) => (
                <Accordion key={medicineId}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            Medicine ID: {medicineId}
                        </Typography>
                        <Box sx={{ marginLeft: 2 }}>
                            <Typography variant="body2">ATC: {medData.atc_code}</Typography>
                            <Typography variant="body2">Name: {medData.atc_display}</Typography>
                        </Box>
                    </AccordionSummary>

                    <AccordionDetails>
                        {Object.entries(medData.medicine_id_part).map(([partId, partData]) => (
                            <Accordion key={partId}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography>Continuum Part: {partId}</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    {partData.medication_requests.map((req, idx) => (
                                        <Box key={req.id || idx} sx={{ mb: 1, p: 1, border: '1px solid #ccc', borderRadius: 2 }}>
                                            <Typography variant="body2">ID: {req.id}</Typography>
                                            <Typography variant="body2">Authored On: {req.authored_on}</Typography>
                                            <Typography variant="body2">Status: {req.status}</Typography>
                                            <Typography variant="body2">Indications: {req.indications?.join(', ') || 'N/A'}</Typography>
                                            <Typography variant="body2">Adverse Effects: {req.adverse_effects?.map(ae => ae.code).join(', ') || 'None'}</Typography>
                                        </Box>
                                    ))}
                                </AccordionDetails>
                            </Accordion>
                        ))}
                    </AccordionDetails>
                </Accordion>
            ))}
        </Box>
    );
};

export default MedicationTree;
