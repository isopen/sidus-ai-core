import os
import sys
sys.path.append(os.environ.get('SIDUS_AI_CORE_PATH'))
import sidusai.plugins.cocoon as cocoon
from sidusai.plugins.cocoon.values import CocoonStatsValue, CocoonHealthValue, CocoonReportValue

host = os.environ.get('COCOON_HOST', 'localhost')
port = int(os.environ.get('COCOON_PORT', '12000'))

def accept_stats(value: CocoonStatsValue):
    print(f'📊 Cocoon stats received: {value}')

def accept_health(value: CocoonHealthValue):
    print(f'🩺 Cocoon health received: {value}')

def accept_report(value: CocoonReportValue):
    print(f'📋 Cocoon report received: {value}')

if __name__ == '__main__':
    print("🤖 Creating Cocoon monitoring agent...")
    agent = cocoon.CocoonMonitoringAgent(
        host=host,
        port=port,
    )

    print("🔧 Building application...")
    agent.application_build()

    print("📊 Getting Cocoon statistics...")
    agent.get_stats(
        handler=accept_stats
    )

    print("🩺 Checking Cocoon health...")
    agent.check_health(
        handler=accept_health
    )

    print("📋 Getting Cocoon report...")
    agent.get_report(
        handler=accept_report
    )
