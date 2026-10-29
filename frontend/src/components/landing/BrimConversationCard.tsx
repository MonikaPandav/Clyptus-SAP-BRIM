import { useRef, useState } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import { ArrowDown, ArrowUpRight, FileText, Layers, MessageSquare, Sparkles, WalletCards, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cardVariant, transitions } from '../../utils/motionVariants';

const topics = [
  {
    id: 'som',
    title: 'Subscription Management (SOM)',
    code: 'SOM',
    phase: 'Subscription & contract',
    description: 'Subscription orders and provider contracts',
    connection: 'Contract distribution',
    Icon: Layers,
    question: 'How does a subscription order in SAP SOM become a subscription contract and get distributed to FI-CA and SAP Convergent Charging?',
  },
  {
    id: 'cc',
    title: 'Charging & Rating (CC)',
    code: 'SAP CC',
    phase: 'Usage to value',
    description: 'Usage rating and charge plans',
    connection: 'Rated billable items',
    Icon: Zap,
    question: 'How are usage events rated with charge plans in SAP Convergent Charging, and how are the resulting billable items sent to Convergent Invoicing?',
  },
  {
    id: 'ci',
    title: 'Convergent Invoicing (CI)',
    code: 'SAP CI',
    phase: 'Billing & invoicing',
    description: 'Billable items, billing, and invoices',
    connection: 'Invoice postings',
    Icon: FileText,
    question: 'How are billable items grouped and processed through billing and invoicing in SAP Convergent Invoicing?',
  },
  {
    id: 'fica',
    title: 'FI-CA & Financials',
    code: 'FI-CA',
    phase: 'Receivables & settlement',
    description: 'Contract accounts, payments, and clearing',
    connection: '',
    Icon: WalletCards,
    question: 'How do payment lots and clearing control allocate incoming payments to open items in SAP FI-CA?',
  },
];

export function BrimConversationCard() {
  const navigate = useNavigate();
  const reduceMotion = useReducedMotion();
  const hubRef = useRef<HTMLDivElement>(null);
  const inView = useInView(hubRef, { margin: '100px' });
  const [previewId, setPreviewId] = useState(topics[0].id);
  const preview = topics.find(topic => topic.id === previewId) ?? topics[0];
  const askQuestion = (question: string) => navigate('/app', { state: { submitPrompt: question } });

  return (
    <motion.div
      className="possibility-card card-brim-conversation"
      ref={hubRef}
      variants={cardVariant}
      aria-labelledby="brim-conversation-title"
    >
      <div className="card-top-content">
        <span className="card-category-tag brim-hub-kicker"><Sparkles size={13} aria-hidden="true" /> BRIM INTELLIGENCE HUB</span>
        <h3 className="card-headline" id="brim-conversation-title">Your BRIM Landscape, Connected</h3>
        <p className="card-description">From subscription to settlement. Explore the process, then ask Clyptus.AI about any stage.</p>
      </div>
      <div className="brim-hub-map" data-animate={inView && !reduceMotion}>
        <div className="brim-hub-map-heading"><span>SUBSCRIPTION TO SETTLEMENT</span><span>04 STAGES</span></div>
        <ol className="brim-conversation-grid" aria-label="SAP BRIM process stages">
        {topics.map(({ id, title, code, phase, description, connection, Icon, question }, index) => (
          <li key={id}>
          <motion.button
            type="button"
            className={`brim-conversation-topic ${previewId === id ? 'is-highlighted' : ''}`}
            data-brim-topic={id}
            data-sample-question={question}
            aria-label={`Ask Clyptus.AI: ${question}`}
            onClick={() => askQuestion(question)}
            onMouseEnter={() => setPreviewId(id)}
            onFocus={() => setPreviewId(id)}
            whileHover={reduceMotion ? undefined : { x: 2 }}
            whileTap={reduceMotion ? undefined : { scale: 0.99 }}
            transition={transitions.micro}
          >
            <span className="brim-conversation-icon"><Icon size={20} aria-hidden="true" /></span>
            <span className="brim-hub-node-copy">
              <span className="brim-hub-node-meta"><span>0{index + 1} / {phase}</span><span className="brim-hub-code">{code}</span></span>
              <span className="brim-conversation-topic-title">{title}</span>
              <span className="brim-hub-node-description">{description}</span>
            </span>
            <ArrowUpRight className="brim-hub-node-arrow" size={16} aria-hidden="true" />
          </motion.button>
          {connection && <div className="brim-hub-connector" aria-hidden="true"><span className="brim-hub-flow-dot" /><ArrowDown size={12} /><span>{connection}</span></div>}
          </li>
        ))}
        </ol>
        <div className="brim-hub-map-note">A process overview. Select a stage to start a conversation.</div>
      </div>
      <div className="brim-hub-prompt">
        <span className="brim-hub-prompt-label"><MessageSquare size={13} aria-hidden="true" /> EXPLORE WITH CLYPTUS.AI <span>{preview.code}</span></span>
        <p className="brim-conversation-question" aria-live="polite">{preview.question}</p>
        <button type="button" className="brim-conversation-action" onClick={() => askQuestion(preview.question)}>Ask this question <ArrowUpRight size={14} aria-hidden="true" /></button>
      </div>
    </motion.div>
  );
}
