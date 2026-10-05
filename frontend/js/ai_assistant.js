/**
 * SIH26044 — AI Skill Intelligence Assistant Drawer
 */

import { api } from './api.js';

export class AiAssistantDrawer {
  constructor() {
    this.isOpen = false;
    this.messages = [];
  }

  init() {
    const fab = document.getElementById('ai-assistant-fab');
    const drawer = document.getElementById('ai-assistant-drawer');
    const closeBtn = document.getElementById('btn-close-ai-drawer');
    const sendBtn = document.getElementById('btn-ai-send');
    const input = document.getElementById('ai-chat-input');

    if (fab) {
      fab.onclick = () => this.toggleDrawer();
    }
    if (closeBtn) {
      closeBtn.onclick = () => this.toggleDrawer(false);
    }
    if (sendBtn && input) {
      sendBtn.onclick = () => this.sendMessage();
      input.onkeypress = (e) => {
        if (e.key === 'Enter') this.sendMessage();
      };
    }

    // Attach Prompt Chips
    document.querySelectorAll('.prompt-chip').forEach(chip => {
      chip.onclick = () => {
        const queryText = chip.innerText.replace(/^[^\w]+/, '').trim();
        if (input) {
          input.value = queryText;
          this.sendMessage();
        }
      };
    });
  }

  toggleDrawer(forceState) {
    const drawer = document.getElementById('ai-assistant-drawer');
    if (!drawer) return;

    this.isOpen = (forceState !== undefined) ? forceState : !this.isOpen;
    if (this.isOpen) {
      drawer.classList.add('open');
      document.getElementById('ai-chat-input')?.focus();
    } else {
      drawer.classList.remove('open');
    }
  }

  async sendMessage(customText = null) {
    const input = document.getElementById('ai-chat-input');
    const text = customText || (input ? input.value.trim() : '');
    if (!text) return;

    if (input) input.value = '';

    // Add user message
    this.addMessageToUI('user', text);

    // Show typing bubble
    const typingId = this.addMessageToUI('bot', '<i class="fa-solid fa-spinner fa-spin"></i> Querying platform intelligence database...');

    try {
      const res = await api.post('/api/ai-assistant/query', { query: text });
      this.removeMessageFromUI(typingId);

      // Render bot reply
      this.addMessageToUI('bot', res.reply, res.action_draft);

      // Check if navigation required
      if (res.navigation_target && window.navigateToTab) {
        window.navigateToTab(res.navigation_target);
      }
    } catch (err) {
      this.removeMessageFromUI(typingId);
      this.addMessageToUI('bot', `⚠️ Assistant error: ${err.message}`);
    }
  }

  addMessageToUI(sender, text, actionDraft = null) {
    const messagesContainer = document.getElementById('ai-drawer-messages');
    if (!messagesContainer) return null;

    const msgId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4);
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.id = msgId;

    // Format markdown bold & bullet lines
    const formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br />');

    let content = `<div>${formatted}</div>`;

    // If there is an action draft, render the confirmation card (WOW Feature #10)
    if (actionDraft) {
      content += `
        <div class="action-card">
          <div style="font-weight:700; color:var(--accent-cyan); font-size:0.85rem; margin-bottom:4px;">
            <i class="fa-solid fa-bolt"></i> Action Prepared: ${actionDraft.title || 'Platform Intervention'}
          </div>
          <p style="font-size:0.75rem; color:var(--text-muted); margin-bottom:8px;">${actionDraft.description || 'Review parameters and confirm to execute on live platform.'}</p>
          <button class="btn btn-sm btn-success btn-confirm-ai-action" data-action='${JSON.stringify(actionDraft).replace(/'/g, "&apos;")}' style="width:100%; font-size:0.75rem;">
            <i class="fa-solid fa-check"></i> Confirm & Execute Action
          </button>
        </div>
      `;
    }

    bubble.innerHTML = content;
    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Attach handler to confirm button
    if (actionDraft) {
      bubble.querySelector('.btn-confirm-ai-action')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Executing...`;
        try {
          const draft = JSON.parse(btn.dataset.action);
          const execRes = await api.post('/api/ai-assistant/confirm-action', {
            action_type: draft.action_type,
            parameters: draft
          });
          btn.outerHTML = `<div style="color:#34D399; font-weight:700; font-size:0.78rem;"><i class="fa-solid fa-circle-check"></i> ${execRes.message}</div>`;
          window.showToast?.(execRes.message, 'success');
        } catch (err) {
          btn.disabled = false;
          btn.innerHTML = `<i class="fa-solid fa-check"></i> Retry Confirmation`;
          window.showToast?.(err.message, 'danger');
        }
      });
    }

    return msgId;
  }

  removeMessageFromUI(msgId) {
    const el = document.getElementById(msgId);
    if (el) el.remove();
  }
}

export const aiAssistant = new AiAssistantDrawer();
