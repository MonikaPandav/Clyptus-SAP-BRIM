import React from 'react';
import {
  Boxes,
  Cpu,
  Database,
  FileSpreadsheet,
  Globe,
  Radio,
  Server,
  Zap,
} from 'lucide-react';

const partners = [
  { name: 'SAP S/4HANA Enterprise', icon: Server },
  { name: 'Convergent Charging (CC)', icon: Zap },
  { name: 'Convergent Invoicing (CI)', icon: FileSpreadsheet },
  { name: 'Contract Accounts (FI-CA)', icon: Database },
  { name: 'Subscription Order Mgmt (SOM)', icon: Boxes },
  { name: 'Telecommunications & 5G', icon: Radio },
  { name: 'Utilities & Smart Grid', icon: Cpu },
  { name: 'Global Cloud Subscription', icon: Globe },
];

export const EnterprisePartnerTicker: React.FC = () => {
  return (
    <div className="partner-ticker-wrap">
      <div className="partner-ticker-inner">
        <div className="partner-ticker-track">
          {partners.concat(partners).map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="partner-item">
                <Icon size={15} className="partner-icon" />
                <span>{item.name}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
