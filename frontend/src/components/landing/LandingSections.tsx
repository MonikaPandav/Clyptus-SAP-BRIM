import './landingSections.css';
import { useEffect } from 'react';
import { EnterprisePartnerTicker } from './EnterprisePartnerTicker';
import { InfinitePossibilitiesGrid } from './InfinitePossibilitiesGrid';
import { BrimModuleExplorer } from './BrimModuleExplorer';
import { AboutClyptusSection } from './AboutClyptusSection';
import { FaqSection } from './FaqSection';
import { FinalCtaSection } from './FinalCtaSection';

export default function LandingSections() {
  useEffect(() => {
    // Keep other lazy section anchors working; About deliberately opens at (0, 0).
    const id = window.location.hash.slice(1);
    if (id && id !== 'about') document.getElementById(id)?.scrollIntoView();
  }, []);

  return (
    <>
      <EnterprisePartnerTicker />
      <InfinitePossibilitiesGrid />
      <BrimModuleExplorer />
      <AboutClyptusSection />
      <FaqSection />
      <FinalCtaSection />
    </>
  );
}
