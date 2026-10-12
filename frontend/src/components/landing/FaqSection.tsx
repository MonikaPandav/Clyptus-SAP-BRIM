import React from 'react';
import { Plus } from 'lucide-react';

const faqs: Array<[string, React.ReactNode]> = [
  ['What is Clyptus.AI?', <><strong>Clyptus.AI</strong> is an enterprise AI knowledge assistant for SAP. It retrieves relevant indexed knowledge before generating an answer, with a dedicated focus on <strong>SAP BRIM</strong>.</>],
  ['What does “RAG-powered” mean?', <><strong>Retrieval-Augmented Generation</strong> retrieves relevant SAP knowledge and provides it as context to an AI model before generating an answer, eliminating <strong>guesswork and hallucination</strong>.</>],
  ['Which SAP BRIM areas does it support?', <>Its BRIM focus includes <strong>Convergent Mediation (CM)</strong>, <strong>Convergent Charging (CC)</strong>, <strong>Convergent Invoicing (CI)</strong>, <strong>Contract Accounts (FI-CA)</strong>, and <strong>Subscription Order Management (SOM)</strong>.</>],
  ['Can I see sources and confidence?', <>Supporting sources and confidence or grounding scores are shown with <strong>every response</strong>. Citations link directly to <strong>verified documentation chunks and exact pages</strong>.</>],
  ['How does generation work?', <>The assistant streams responses <strong>token-by-token</strong> with <strong>real-time thinking status indicators</strong> and automated grounding verification.</>],
  ['What if the available knowledge cannot answer?', <>The assistant strictly respects enterprise domain boundaries, <strong>declining out-of-scope non-SAP requests</strong> and alerting when <strong>knowledge is insufficient</strong>.</>],
];

export const FaqSection: React.FC = () => {
  return (
    <section className="section faq-section" id="faq">
      <div className="section-heading">
        <span className="eyebrow">A FEW GOOD QUESTIONS</span>
        <h2>Curious? <span>We thought so.</span></h2>
      </div>
      <div className="faq-list">
        {faqs.map(([question, answer]) => (
          <details className="faq-item" key={question}>
            <summary>
              {question}
              <Plus size={18} aria-hidden="true" />
            </summary>
            <p>{answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
};
