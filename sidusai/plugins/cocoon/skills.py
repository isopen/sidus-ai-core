from sidusai.plugins.cocoon.components import CocoonMonitoringComponent
from sidusai.plugins.cocoon.values import CocoonStatsValue, CocoonHealthValue, CocoonReportValue

def cocoon_get_detailed_stats_skill(value: CocoonStatsValue, client: CocoonMonitoringComponent) -> CocoonStatsValue:
    result = client.get_json_stats()
    print(f"Cocoon detailed stats: {result}")
    return value

def cocoon_check_worker_skill(value: CocoonHealthValue, client: CocoonMonitoringComponent) -> CocoonHealthValue:
    result = client.check_worker_status()

    if result.get("available"):
        print("Cocoon worker is responding")
    else:
        print("Cocoon worker is not responding")

    return value

def cocoon_get_comprehensive_report_skill(value: CocoonReportValue, client: CocoonMonitoringComponent) -> CocoonReportValue:
    result = client.get_comprehensive_stats()
    print(f"Cocoon comprehensive report: {result}")
    return value
