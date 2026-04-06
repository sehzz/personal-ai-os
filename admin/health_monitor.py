


from datetime import datetime

from lib.database import Database
from managers.base import ManagerRequest
from managers.content.manager import ContentManager
from managers.finance.manager import FinanceManager
from managers.life_admin.manager import LifeAdminManager
from managers.relationship.manager import RelationshipManager


class HealthMonitor:
    def __init__(self, managers: dict):
        self.managers = managers
        self.db = Database(app_name="ollama")

    def check_all(self):
        """Check the health of all managers and update the database with their status."""

        status = None
        error = None

        for name, manager in self.managers.items():
            try:
                manager.process(ManagerRequest(task="ping", context={}))
                status = "healthy"
            except Exception as e:
                print(f"Manager {name} is unhealthy: {e}")
                status = "offline"
                error = str(e)
            
            payload = {
                "manager": name,
                "status": status,
                "last_seen_at": datetime.now().isoformat(),
                "last_error": error,
            }
            self.db.update_data_in_table(table_name="admin_manager_health", manager=name, data=payload)              
    
    def get_status(self, manager_name: str):
        """
        Get the health status of a specific manager from the database.
        
        Args:
            manager_name (str): The name of the manager to check.  

        Returns:
            dict: A dictionary containing the manager's health status and related information, or None if the manager is not found.
        """
        response = self.db.get_data_from_table(table_name="admin_manager_health")
        for manager_data in response:
            if manager_data.get("manager") == manager_name:
                
                return manager_data
            
        return None


if __name__ == "__main__":
    monitor = HealthMonitor({'finance': FinanceManager(), 'content': ContentManager(), 'relationships': RelationshipManager(), 'life_admin': LifeAdminManager()})
    # monitor.check_all()
    a = monitor.get_status("finance")
    print(a)