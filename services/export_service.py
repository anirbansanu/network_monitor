# services/export_service.py
"""
Service for exporting data to external formats (CSV, JSON).
"""

import csv
from typing import List
from models.data_models import FlowStat, InterfaceStat


class ExportService:
    """
    Handles data export operations.
    """
    
    @staticmethod
    def export_flows_to_csv(filepath: str, flows: List[FlowStat]) -> bool:
        """
        Export a list of FlowStat objects to a CSV file.
        """
        if not flows:
            return False
            
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow([
                    "Timestamp", "Protocol", "Local IP", "Local Port",
                    "Remote IP", "Remote Port", "Bytes Up", "Bytes Down",
                    "Process", "PID"
                ])
                
                # Rows
                for flow in flows:
                    writer.writerow([
                        flow.last_seen.isoformat(),
                        flow.protocol.value,
                        flow.local_ip,
                        flow.local_port,
                        flow.remote_ip,
                        flow.remote_port,
                        flow.bytes_up,
                        flow.bytes_down,
                        flow.process_name or "",
                        flow.process_pid or ""
                    ])
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
