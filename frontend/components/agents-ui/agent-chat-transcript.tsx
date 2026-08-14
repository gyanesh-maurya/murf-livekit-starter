'use client';

import { type ComponentProps } from 'react';
import { AnimatePresence } from 'motion/react';
import { type AgentState, type ReceivedMessage } from '@livekit/components-react';
import { AgentChatIndicator } from '@/components/agents-ui/agent-chat-indicator';
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation';
import { Message, MessageContent, MessageResponse } from '@/components/ai-elements/message';

/**
 * Props for the AgentChatTranscript component.
 */
export interface AgentChatTranscriptProps extends ComponentProps<'div'> {
  /**
   * The current state of the agent. When 'thinking', displays a loading indicator.
   */
  agentState?: AgentState;
  /**
   * Array of messages to display in the transcript.
   * @defaultValue []
   */
  messages?: ReceivedMessage[];
  /**
   * Additional CSS class names to apply to the conversation container.
   */
  className?: string;
}

/**
 * A chat transcript component that displays a conversation between the user and agent.
 * Shows messages with timestamps and origin indicators, plus a thinking indicator
 * when the agent is processing.
 *
 * @extends ComponentProps<'div'>
 *
 * @example
 * ```tsx
 * <AgentChatTranscript
 *   agentState={agentState}
 *   messages={chatMessages}
 * />
 * ```
 */
export function AgentChatTranscript({
  agentState,
  messages = [],
  className,
  ...props
}: AgentChatTranscriptProps) {
  let activeAgentTracker: 'DukaanSaathi' | 'SevaSaathi' = 'DukaanSaathi';
  let pendingSwitch: 'DukaanSaathi' | 'SevaSaathi' | null = null;

  return (
    <Conversation className={className} {...props}>
      <ConversationContent>
        {messages.map((receivedMessage) => {
          const { id, timestamp, from, message } = receivedMessage;
          const isUser = from?.isLocal === true;
          const time = new Date(timestamp);
          const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

          // Track agent transitions:
          // - When DukaanSaathi announces transfer ("ट्रांसफर कर रही"), the NEXT agent messages are from SevaSaathi
          // - When SevaSaathi announces hand-back ("वापस दुकानसाथी"), the NEXT agent messages are from DukaanSaathi
          if (!isUser) {
            if (pendingSwitch === 'SevaSaathi') {
              // This is the first agent message AFTER the transfer announcement = SevaSaathi speaking
              activeAgentTracker = 'SevaSaathi';
              pendingSwitch = null;
            } else if (pendingSwitch === 'DukaanSaathi') {
              activeAgentTracker = 'DukaanSaathi';
              pendingSwitch = null;
            }

            // Detect transfer announcement from DukaanSaathi
            if (
              message.includes('सेवासाथी के पास ट्रांसफर') ||
              message.includes('ट्रांसफर कर रही')
            ) {
              // Mark: next agent message will be from SevaSaathi
              pendingSwitch = 'SevaSaathi';
            }
            // Detect hand-back announcement from SevaSaathi
            if (
              message.includes('वापस दुकानसाथी') ||
              message.includes('दुकानसाथी के पास ट्रांसफर')
            ) {
              pendingSwitch = 'DukaanSaathi';
            }
          }

          // Assign current message sender based on tracker at the moment of this message
          const currentMessageSender = isUser
            ? 'User'
            : activeAgentTracker;

          const senderName = isUser
            ? 'You (Customer)'
            : currentMessageSender === 'SevaSaathi'
            ? 'SevaSaathi (Returns & Refunds Specialist)'
            : 'DukaanSaathi (Main Store Assistant)';

          const badgeLabel = isUser
            ? 'Customer'
            : currentMessageSender === 'SevaSaathi'
            ? 'Returns Specialist'
            : 'Main Assistant';

          const badgeStyle = isUser
            ? 'bg-slate-800 text-slate-300 border-slate-700'
            : currentMessageSender === 'SevaSaathi'
            ? 'bg-rose-500/20 text-rose-300 border-rose-500/30 font-semibold'
            : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30 font-semibold';

          const avatarBg = isUser
            ? 'bg-indigo-600'
            : currentMessageSender === 'SevaSaathi'
            ? 'bg-rose-600'
            : 'bg-emerald-600';

          const avatarInitial = isUser ? 'U' : currentMessageSender === 'SevaSaathi' ? 'S' : 'D';

          return (
            <div key={id} className="flex flex-col space-y-1 my-2.5">
              {/* Message Header: Avatar + Sender Name + Badge Tag + Timestamp */}
              <div className={`flex items-center gap-2 text-xs ${isUser ? 'justify-end pr-2' : 'justify-start pl-2'}`}>
                {!isUser && (
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-sm ${avatarBg}`}>
                    {avatarInitial}
                  </div>
                )}
                <span className="font-semibold text-slate-200">{senderName}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-md border ${badgeStyle}`}>
                  {badgeLabel}
                </span>
                <span className="text-[10px] text-slate-400">({timeStr})</span>
                {isUser && (
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-sm ${avatarBg}`}>
                    {avatarInitial}
                  </div>
                )}
              </div>

              {/* Message Bubble Content */}
              <Message title={timeStr} from={isUser ? 'user' : 'assistant'}>
                <MessageContent>
                  <MessageResponse>{message}</MessageResponse>
                </MessageContent>
              </Message>
            </div>
          );
        })}
        <AnimatePresence>
          {agentState === 'thinking' && <AgentChatIndicator size="sm" />}
        </AnimatePresence>
      </ConversationContent>
      <ConversationScrollButton />
    </Conversation>
  );
}
