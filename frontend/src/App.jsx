import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  FileCheck2,
  FileText,
  GraduationCap,
  History,
  Info,
  LifeBuoy,
  LoaderCircle,
  Menu,
  MessageCircle,
  Plus,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Trash2,
  UserRound,
  X,
} from "lucide-react";

const navigation = [
  { id: "assistant", label: "Ask CampusIQ", icon: MessageCircle, group: "Workspace" },
  { id: "handbook", label: "Handbook search", icon: BookOpen, group: "Workspace" },
  { id: "cases", label: "My support cases", icon: FileCheck2, group: "My services" },
  { id: "timetable", label: "My timetable", icon: CalendarDays, group: "My services" },
  { id: "chats", label: "Chat history", icon: MessageCircle, group: "My services" },
  { id: "history", label: "Search history", icon: History, group: "My services" },
  { id: "about", label: "About CampusIQ", icon: CircleHelp, group: "Information" },
];

async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    credentials: "same-origin",
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || "Something went wrong. Please try again.");
    error.status = response.status;
    throw error;
  }
  return payload;
}

function initials(name = "Student") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function App() {
  const [session, setSession] = useState(null);
  const [students, setStudents] = useState([]);
  const [page, setPage] = useState("assistant");
  const [cases, setCases] = useState([]);
  const [timetable, setTimetable] = useState(null);
  const [searches, setSearches] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const loadSession = useCallback(async () => {
    try {
      const [current, roster] = await Promise.all([
        api("/session"),
        api("/demo-students"),
      ]);
      setStudents(roster);
      if (current.authenticated) {
        setSession(current);
        setActiveConversationId(current.active_conversation_id || null);
        if (current.active_conversation_id) {
          const transcript = await api(`/conversations/${current.active_conversation_id}/messages`);
          setChatMessages(transcript.messages.map((item) => ({
            role: item.role,
            text: item.text,
            draft: item.metadata?.draft,
            canApprove: item.can_approve,
          })));
        }
        if (current.awaiting_approval && current.pending_draft) {
          setChatMessages((messages) =>
            messages.length
              ? messages
              : [
                  {
                    role: "assistant",
                    text: "You have a support-case draft waiting for your decision.",
                    draft: current.pending_draft,
                  },
                ],
          );
        }
      }
    } catch (requestError) {
      setError(requestError.message);
    }
  }, []);

  const refreshSearchHistory = useCallback(async () => {
    const result = await api("/search-history");
    setSearches(result.searches);
  }, []);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  useEffect(() => {
    if (!session) return;
    let active = true;
    setError("");
    const loadPage = async () => {
      try {
        if (page === "cases") {
          const result = await api("/cases");
          if (active) setCases(result.cases);
        } else if (page === "timetable") {
          const result = await api("/timetable");
          if (active) setTimetable(result.timetable);
        } else if (page === "history") {
          const result = await api("/search-history");
          if (active) setSearches(result.searches);
        } else if (page === "chats") {
          const result = await api("/conversations");
          if (active) setConversations(result.conversations);
        } else if (page === "handbook") {
          const [documentsResult, searchesResult] = await Promise.all([
            api("/handbook/documents"),
            api("/search-history"),
          ]);
          if (active) {
            setDocuments(documentsResult.documents);
            setSearches(searchesResult.searches);
          }
        }
      } catch (requestError) {
        if (requestError.status === 401) {
          setSession(null);
          setChatMessages([]);
        } else {
          setError(requestError.message);
        }
      }
    };
    loadPage();
    return () => {
      active = false;
    };
  }, [page, session]);

  const signIn = async (studentId) => {
    setBusy(true);
    setError("");
    try {
      const result = await api("/session", {
        method: "POST",
        body: JSON.stringify({ student_id: studentId }),
      });
      setSession({
        authenticated: true,
        student: result.student,
        awaiting_approval: false,
        model_provider: "Gemini",
        model_configured: result.model_configured,
      });
      setPage("assistant");
      setChatMessages([]);
      setActiveConversationId(null);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const signOut = async () => {
    try {
      await api("/logout", { method: "POST" });
    } catch (requestError) {
      setError(requestError.message);
    }
    setSession(null);
    setChatMessages([]);
    setActiveConversationId(null);
    setPage("assistant");
  };

  const sendMessage = async (message) => {
    const clean = message.trim();
    if (!clean || busy) return;
    setChatMessages((items) => [...items, { role: "user", text: clean }]);
    setBusy(true);
    setError("");
    try {
      const result = await api("/chat", {
        method: "POST",
        body: JSON.stringify({
          message: clean,
          conversation_id: activeConversationId,
        }),
      });
      setActiveConversationId(result.conversation_id);
      setChatMessages((items) => [
        ...items.map((item) => item.canApprove ? { ...item, canApprove: false } : item),
        {
          role: "assistant",
          text: result.message,
          draft: result.pending_draft,
          canApprove: result.awaiting_approval,
        },
      ]);
      setSession((current) => ({
        ...current,
        awaiting_approval: result.awaiting_approval,
        run_status: result.run_status,
      }));
      try {
        const history = await api("/conversations");
        setConversations(history.conversations);
      } catch {
        setError("Your response was received, but chat history could not be refreshed.");
      }
      return true;
    } catch (requestError) {
      setChatMessages((items) => [
        ...items,
        { role: "assistant", text: requestError.message, isError: true },
      ]);
      if (requestError.status === 401) setSession(null);
      return false;
    } finally {
      setBusy(false);
    }
  };

  const runSearch = async (query) => {
    const result = await api("/handbook/search", {
      method: "POST",
      body: JSON.stringify({ query }),
    });
    return result;
  };

  const choosePage = (next) => {
    setPage(next);
    setNavOpen(false);
  };

  const startNewChat = async () => {
    setBusy(true);
    setError("");
    try {
      const created = await api("/conversations", { method: "POST" });
      setActiveConversationId(created.conversation_id);
      setChatMessages([]);
      choosePage("assistant");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const openConversation = async (conversationId) => {
    setBusy(true);
    setError("");
    try {
      const transcript = await api(`/conversations/${conversationId}/open`, {
        method: "POST",
      });
      setActiveConversationId(conversationId);
      setChatMessages(transcript.messages.map((item) => ({
        role: item.role,
        text: item.text,
        draft: item.metadata?.draft,
        canApprove: item.can_approve,
      })));
      choosePage("assistant");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const removeConversation = async (conversationId) => {
    try {
      await api(`/conversations/${conversationId}`, { method: "DELETE" });
      setConversations((items) => items.filter((item) => item.id !== conversationId));
      if (activeConversationId === conversationId) {
        setActiveConversationId(null);
        setChatMessages([]);
        setPage("assistant");
      }
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const clearConversations = async () => {
    try {
      await api("/conversations", { method: "DELETE" });
      setConversations([]);
      setChatMessages([]);
      setActiveConversationId(null);
      setPage("assistant");
      setNotice("Your saved conversations have been deleted.");
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  if (!session) {
    return (
      <SignIn
        students={students}
        busy={busy}
        error={error}
        onSignIn={signIn}
        onClearError={() => setError("")}
      />
    );
  }

  const active = navigation.find((item) => item.id === page) || navigation[0];
  const ActiveIcon = active.icon;

  return (
    <div className="app-shell">
      {navOpen && <button className="mobile-scrim" onClick={() => setNavOpen(false)} aria-label="Close navigation" />}
      <aside className={`sidebar ${navOpen ? "sidebar-open" : ""}`}>
        <button className="brand-lockup" onClick={() => choosePage("assistant")} aria-label="CampusIQ home">
          <span className="brand-symbol"><Sparkles size={21} strokeWidth={2.2} /></span>
          <span className="brand-wordmark">campus<span>iq</span></span>
        </button>
        <div className="sidebar-product">STUDENT SUPPORT INTELLIGENCE</div>

        <div className="nav-scroll">
          {["Workspace", "My services", "Information"].map((group) => (
            <section className="nav-group" key={group} aria-label={group}>
              <p className="nav-label">{group}</p>
              {navigation.filter((item) => item.group === group).map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    className={`nav-item ${page === item.id ? "nav-item-active" : ""}`}
                    key={item.id}
                    onClick={() => choosePage(item.id)}
                  >
                    <Icon size={18} strokeWidth={1.8} />
                    <span>{item.label}</span>
                    {item.id === "assistant" && <span className="nav-live-dot" />}
                  </button>
                );
              })}
            </section>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="sidebar-help">
            <div className="help-mark"><LifeBuoy size={18} /></div>
            <div>
              <strong>Need a person?</strong>
              <span>Contact your department office</span>
            </div>
            <ArrowUpRight size={15} />
          </div>
          <div className="sidebar-footer">
            <span className="status-dot" />
            <span>Demo environment</span>
            <span className="version-pill">v1.0</span>
          </div>
        </div>
      </aside>

      <div className="main-column">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu icon-button" onClick={() => setNavOpen(true)} aria-label="Open navigation">
              <Menu size={20} />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span><span className="breadcrumb-slash">/</span>
              <strong><ActiveIcon size={15} />{active.label}</strong>
            </div>
          </div>
          <div className="topbar-right">
            <span className="environment-tag"><span /> Prototype</span>
            <div className="topbar-divider" />
            <button className="user-menu" onClick={signOut} title="Sign out of demo">
              <span className="avatar">{initials(session.student?.name)}</span>
              <span className="user-menu-copy">
                <strong>{session.student?.name?.split(" ")[0] || "Student"}</strong>
                <small>{session.student?.student_id}</small>
              </span>
              <ChevronDown size={15} className="user-chevron" />
            </button>
          </div>
        </header>

        <main className="page-wrap">
          {notice && (
            <div className="toast-success"><CheckCircle2 size={17} />{notice}<button onClick={() => setNotice("")} aria-label="Dismiss confirmation"><X size={15} /></button></div>
          )}
          {error && (
            <div className="alert alert-error" role="alert">
              <Info size={17} /><span>{error}</span><button onClick={() => setError("")} aria-label="Dismiss error"><X size={16} /></button>
            </div>
          )}
          {page === "assistant" && (
            <AssistantPage
              messages={chatMessages}
              busy={busy}
              onSend={sendMessage}
              onNavigate={choosePage}
              session={session}
              onNewChat={startNewChat}
            />
          )}
          {page === "handbook" && (
            <HandbookPage
              documents={documents}
              searches={searches}
              onSearch={runSearch}
              onHistoryRefresh={refreshSearchHistory}
            />
          )}
          {page === "cases" && <CasesPage cases={cases} onNavigate={choosePage} />}
          {page === "timetable" && <TimetablePage timetable={timetable} />}
          {page === "chats" && (
            <ChatsPage
              conversations={conversations}
              onOpen={openConversation}
              onDelete={removeConversation}
              onClear={clearConversations}
              onNewChat={startNewChat}
            />
          )}
          {page === "history" && (
            <HistoryPage
              searches={searches}
              onClear={async () => {
                try {
                  await api("/search-history", { method: "DELETE" });
                  setSearches([]);
                  setNotice("Your handbook search history has been cleared.");
                } catch (requestError) {
                  setError(requestError.message);
                }
              }}
              onNavigate={choosePage}
            />
          )}
          {page === "about" && <AboutPage onNavigate={choosePage} />}
        </main>
        <footer className="app-footer">
          <span>CampusIQ <span className="footer-dot">·</span> A student-support prototype</span>
          <span>Answers are grounded in the project’s approved knowledge collection.</span>
        </footer>
      </div>
    </div>
  );
}

function SignIn({ students, busy, error, onSignIn, onClearError }) {
  const [studentId, setStudentId] = useState("");
  const [selected, setSelected] = useState("");
  useEffect(() => {
    if (selected) setStudentId(selected);
  }, [selected]);

  return (
    <div className="sign-in-page">
      <div className="sign-in-topline">
        <div className="brand-lockup">
          <span className="brand-symbol"><Sparkles size={21} /></span>
          <span className="brand-wordmark">campus<span>iq</span></span>
        </div>
        <span className="environment-tag"><span /> Prototype</span>
      </div>
      <div className="sign-in-layout">
        <section className="sign-in-intro">
          <div className="eyebrow"><span className="eyebrow-line" /> A CALMER WAY TO GET SUPPORT</div>
          <h1>Student support,<br /><span>made clearer.</span></h1>
          <p>Find handbook guidance, check your timetable, and prepare a support case with a human approval step.</p>
          <div className="sign-in-features">
            <div><span className="feature-icon"><BookOpen size={18} /></span><span><strong>Grounded answers</strong><small>Responses draw on the project’s approved knowledge collection.</small></span></div>
            <div><span className="feature-icon"><ShieldCheck size={18} /></span><span><strong>You stay in control</strong><small>A case is only created after you review and approve its draft.</small></span></div>
            <div><span className="feature-icon"><History size={18} /></span><span><strong>Your history</strong><small>Return to saved chats and handbook searches.</small></span></div>
          </div>
          <div className="sign-in-footnote"><span className="tiny-shield"><ShieldCheck size={14} /></span> Built for a synthetic-data demonstration. Not an official university service.</div>
        </section>

        <section className="sign-in-card">
          <div className="login-card-icon"><GraduationCap size={22} /></div>
          <div className="eyebrow login-eyebrow">WELCOME TO CAMPUSIQ</div>
          <h2>Sign in to your demo</h2>
          <p className="login-desc">Choose a sample student profile or enter its student ID to explore the system.</p>
          {error && <div className="alert alert-error login-alert"><Info size={16} /><span>{error}</span><button onClick={onClearError}><X size={15} /></button></div>}
          <label className="field-label" htmlFor="sample-student">Sample student profile</label>
          <div className="select-wrap">
            <UserRound size={17} />
            <select id="sample-student" value={selected} onChange={(event) => setSelected(event.target.value)}>
              <option value="">Select a demo profile…</option>
              {students.map((student) => (
                <option key={student.student_id} value={student.student_id}>
                  {student.name} · {student.student_id}
                </option>
              ))}
            </select>
            <ChevronDown size={15} />
          </div>
          <div className="field-or"><span />or enter a student ID<span /></div>
          <label className="field-label" htmlFor="student-id">Student ID</label>
          <div className="input-wrap">
            <UserRound size={17} />
            <input
              id="student-id"
              inputMode="numeric"
              maxLength={10}
              placeholder="e.g. 2300701098"
              value={studentId}
              onChange={(event) => { setSelected(""); setStudentId(event.target.value.replace(/\D/g, "")); }}
              onKeyDown={(event) => { if (event.key === "Enter" && studentId) onSignIn(studentId); }}
            />
          </div>
          <button className="button button-primary sign-in-submit" disabled={busy || studentId.length !== 10} onClick={() => onSignIn(studentId)}>
            {busy ? <LoaderCircle className="spin" size={17} /> : <>Continue to CampusIQ <ArrowRight size={17} /></>}
          </button>
          <div className="demo-notice"><Info size={16} /><span><strong>Demo sign-in, not secure authentication.</strong> Anyone with a sample ID can access that sample profile. Use fictional data only.</span></div>
        </section>
      </div>
      <div className="login-bottom"><span>CAMPUSIQ <span>·</span> Student support assistant</span><span>Educational prototype <span>·</span> 2026</span></div>
    </div>
  );
}

function PageHeading({ eyebrow, title, description, action }) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}

function StatusBadge({ status }) {
  const value = status || "Unknown";
  const kind = value.toLowerCase().replaceAll(" ", "-");
  return <span className={`status-badge status-${kind}`}><span />{value}</span>;
}

function EmptyInline({ icon: Icon, title, text, action, onClick }) {
  return (
    <div className="empty-inline">
      <span className="empty-icon"><Icon size={20} /></span><div><strong>{title}</strong><p>{text}</p></div>
      {action && <button className="text-button" onClick={onClick}>{action}<ArrowRight size={14} /></button>}
    </div>
  );
}

function AssistantPage({ messages, busy, onSend, onNavigate, session, onNewChat }) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  const submit = async (event) => {
    event?.preventDefault();
    const clean = draft.trim();
    if (!clean || busy) return;
    setDraft("");
    await onSend(clean);
  };
  const prompts = [
    "How many times can I retake a failed course?",
    "Show me my timetable",
    "I need to file a case about missing marks",
  ];

  return (
    <div className="page-content assistant-content">
      <PageHeading
        eyebrow="CAMPUSIQ ASSISTANT"
        title="How can I help?"
        description="Gemini proposes steps for supported case workflows; code validates every action and requires your approval. Handbook answers use retrieved sources. Your conversations are saved for your reference."
        action={<div className="assistant-heading-actions"><button className="button button-secondary" onClick={() => onNavigate("chats")}><History size={15} /> Chat history</button><button className="button button-primary" onClick={onNewChat}><Plus size={15} /> New chat</button></div>}
      />
      <div className="assistant-layout">
        <section className="chat-panel surface-card">
          <div className="chat-topline">
            <div className="assistant-identity"><span className="assistant-avatar"><Sparkles size={18} /></span><span><strong>CampusIQ</strong><small><span className="status-dot" /> {session.model_configured ? "Gemini planner ready" : "AI setup needed · contact support"}</small></span></div>
            <div className="chat-top-badge"><ShieldCheck size={14} /> Bounded assistant</div>
          </div>
          <div className="chat-scroll">
            {messages.length === 0 ? (
              <div className="chat-welcome">
                <div className="chat-welcome-mark"><Sparkles size={25} /></div>
                <div className="chat-time-label">YOUR STUDENT SUPPORT ASSISTANT</div>
                <h2>Let’s find your next step.</h2>
                <p>I can search approved guidance, look up your own timetable or case, and help prepare a draft for staff review.</p>
                <div className="suggestion-grid">
                  {prompts.map((prompt) => <button key={prompt} onClick={() => setDraft(prompt)}>{prompt}<ArrowUpRight size={14} /></button>)}
                </div>
              </div>
            ) : (
              <div className="message-list">
                <div className="conversation-divider"><span />TODAY<span /></div>
                {messages.map((message, index) => (
                  <ChatMessage key={`${index}-${message.role}`} message={message} onSend={onSend} busy={busy} />
                ))}
                {busy && <div className="message-row assistant-row"><span className="message-avatar"><Sparkles size={14} /></span><div className="typing-bubble"><i /><i /><i /></div></div>}
              </div>
            )}
            <div ref={(node) => { bottomRef.current = node; }} />
          </div>
          <form className="chat-compose" onSubmit={submit}>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask a question or tell CampusIQ what you need…"
              rows={1}
              maxLength={1000}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submit();
                }
              }}
              aria-label="Message CampusIQ"
            />
            <div className="compose-bottom"><span><span className="compose-lock"><ShieldCheck size={12} /></span> Avoid sharing passwords or sensitive personal information.</span><button className="send-button" type="submit" disabled={!draft.trim() || busy} aria-label="Send message">{busy ? <LoaderCircle className="spin" size={17} /> : <Send size={17} />}</button></div>
          </form>
          <div className="chat-disclaimer">CampusIQ is a prototype. It does not decide admissions, grades, fees, or disciplinary outcomes.</div>
        </section>
        <aside className="assistant-aside">
          <section className="surface-card sidebar-info-card">
            <div className="aside-heading"><span className="aside-heading-icon"><Sparkles size={16} /></span><h3>What CampusIQ can do</h3></div>
            <div className="capability-item"><span className="capability-check"><Check size={13} /></span><span><strong>Answer policy questions</strong><small>From the approved knowledge collection, with citations.</small></span></div>
            <div className="capability-item"><span className="capability-check"><Check size={13} /></span><span><strong>Look up your services</strong><small>Only your own sample timetable and case information.</small></span></div>
            <div className="capability-item"><span className="capability-check"><Check size={13} /></span><span><strong>Prepare a support case</strong><small>Review the exact draft; approval is required to submit.</small></span></div>
            <div className="aside-divider" />
            <div className="human-note"><ShieldCheck size={16} /><span>Case decisions and status changes remain with staff.</span></div>
          </section>
          <section className="source-aside-card">
            <span className="source-aside-icon"><BookOpen size={18} /></span><div><strong>Need a direct search?</strong><p>Search across the student support knowledge documents yourself.</p><button className="text-button" onClick={() => onNavigate("handbook")}>Open handbook <ArrowRight size={14} /></button></div>
          </section>
          <div className="session-card"><span className="avatar avatar-small">{initials(session.student?.name)}</span><span><small>DEMO SESSION</small><strong>{session.student?.student_id}</strong></span><span className="session-active"><i /> Active</span></div>
        </aside>
      </div>
    </div>
  );
}

function ChatMessage({ message, onSend, busy }) {
  const [decisionSent, setDecisionSent] = useState(false);
  if (message.role === "user") {
    return <div className="message-row user-row"><div className="message-bubble user-bubble">{message.text}</div><span className="user-message-avatar">{initials()}</span></div>;
  }
  return (
    <div className="message-row assistant-row">
      <span className="message-avatar"><Sparkles size={14} /></span>
      <div className={`message-bubble assistant-bubble ${message.isError ? "message-error" : ""}`}>
        <div className="message-author">CampusIQ <span>·</span> {message.isError ? "Notice" : "Assistant"}</div>
        <div className="message-text">{message.text}</div>
        {message.draft && (
          <div className="pending-draft">
            <div className="pending-draft-heading"><FileCheck2 size={15} /><strong>{message.canApprove ? "Draft waiting for your approval" : "Saved support-case draft"}</strong></div>
            <span><b>Category</b>{message.draft.category?.replaceAll("_", " ")}</span>
            <span><b>Description</b>{message.draft.description}</span>
            {message.canApprove ? (
              <>
                <div className="approval-actions">
                  <button className="button button-primary button-small" disabled={busy || decisionSent} onClick={async () => { if (await onSend("yes")) setDecisionSent(true); }}>Approve this draft</button>
                  <button className="button button-secondary button-small" disabled={busy || decisionSent} onClick={async () => { if (await onSend("no")) setDecisionSent(true); }}>No, not yet</button>
                </div>
                <div className="approval-hint"><ShieldCheck size={13} /> A case is created only after you confirm.</div>
              </>
            ) : <div className="approval-hint"><ShieldCheck size={13} /> Saved for reference. To submit a case, start a new request.</div>}
          </div>
        )}
        {!message.draft && message.text.includes("[Source:") && <div className="message-citation"><BookOpen size={13} /> Approved knowledge source cited in response</div>}
      </div>
    </div>
  );
}

function HandbookPage({ documents, searches, onSearch, onHistoryRefresh }) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const popular = ["Retake policy", "Missing marks", "Registration deadlines", "Data privacy"];

  const search = async (event) => {
    event?.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    setError("");
    try {
      const response = await onSearch(query.trim());
      setResult(response);
      await onHistoryRefresh();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <PageHeading eyebrow="APPROVED KNOWLEDGE" title="Search the handbook" description="Find guidance from the project’s curated student-support documents. Searches are saved to your history, so avoid entering personal details." />
      <section className="handbook-search-hero">
        <div className="handbook-search-content">
          <div className="search-badge"><BookOpen size={14} /> GROUNDED IN APPROVED DOCUMENTS</div>
          <h2>What would you like<br />to know?</h2>
          <p>Search policies and course guidance with source context you can check.</p>
          <form className="handbook-search-form" onSubmit={search}>
            <Search size={19} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="e.g. How many times can I retake a course?" maxLength={300} aria-label="Search approved documents" />
            <button className="button button-primary" disabled={loading || !query.trim()}>{loading ? <LoaderCircle className="spin" size={17} /> : <>Search <ArrowRight size={15} /></>}</button>
          </form>
          <div className="popular-searches"><span>Try:</span>{popular.map((item) => <button key={item} onClick={() => setQuery(item)}>{item}</button>)}</div>
          {error && <div className="search-error">{error}</div>}
        </div>
        <div className="handbook-search-art" aria-hidden="true"><div className="search-art-orbit" /><div className="search-art-book"><BookOpen size={49} strokeWidth={1.1} /></div><div className="search-art-tag tag-one">DOC-02</div><div className="search-art-tag tag-two"><Check size={14} /> Source verified</div></div>
      </section>

      {result ? (
        <section className="search-result-layout">
          <div className="surface-card answer-card">
            <div className="answer-card-header"><span className={`decision-icon decision-${result.decision}`}><CheckCircle2 size={18} /></span><span><small>CAMPUSIQ RESPONSE</small><strong>{decisionTitle(result.decision)}</strong></span><button className="icon-button answer-close" onClick={() => setResult(null)} aria-label="Close search result"><X size={17} /></button></div>
            <div className="answer-copy">{result.answer}</div>
            {result.sources?.length > 0 && <div className="citation-row"><span>Sources</span>{result.sources.map((source) => <span className="citation-chip" key={source}><BookOpen size={12} />{source}</span>)}</div>}
          </div>
          <div className="surface-card matched-sources">
            <div className="card-heading"><div><h2>Relevant passages</h2><p>Retrieved evidence, ranked by relevance.</p></div><span className="count-pill">{result.results.length}</span></div>
            {result.results.length ? result.results.map((item) => (
              <div className="source-result" key={`${item.doc_id}-${item.title}`}>
                <div className="source-result-top"><span className="source-document-icon"><FileText size={15} /></span><span><strong>{item.title}</strong><small>{item.doc_id}</small></span><span className="score-pill">{Math.round(item.score * 100)}% match</span></div>
                <p>{item.excerpt}{item.excerpt.length >= 360 ? "…" : ""}</p>
              </div>
            )) : <EmptyInline icon={Search} title="No passages met the match threshold" text="CampusIQ has not found relevant evidence for this search. Try clearer wording or check with your department office." />}
          </div>
        </section>
      ) : (
        <div className="handbook-lower-grid">
          <section className="surface-card doc-library">
            <div className="card-heading"><div><h2>Knowledge collection</h2><p>{documents.length} curated documents available to search.</p></div><span className="doc-count">{documents.length} docs</span></div>
            <div className="doc-list">
              {documents.map((doc) => (
                <div className="doc-row" key={doc.id}><span className="doc-id-mark">{doc.id.replace("DOC-", "")}</span><span><strong>{doc.title}</strong><small>Approved knowledge source · {doc.id}</small></span><ArrowUpRight size={15} /></div>
              ))}
            </div>
          </section>
          <section className="surface-card recent-search-card">
            <div className="card-heading"><div><h2>Recent searches</h2><p>Saved to your demo account.</p></div><History size={17} className="muted-icon" /></div>
            {searches.length ? (
              <div className="recent-search-list">{searches.slice(0, 5).map((item) => <button className="recent-search-item" key={item.id} onClick={() => setQuery(item.query)}><span className="recent-search-icon"><Search size={14} /></span><span><strong>{item.query}</strong><small>{formatDate(item.created_at)} · {item.sources.join(", ") || "No source"}</small></span><ArrowUpRight size={14} /></button>)}</div>
            ) : <div className="recent-empty"><History size={21} /><span>Your searches will appear here after you search.</span></div>}
            <div className="privacy-inline"><ShieldCheck size={14} /> Search metadata is saved here; full conversations are kept separately in Chat history.</div>
          </section>
        </div>
      )}
      {!result && <div className="handbook-footnote"><Info size={14} /> Documents are team-synthesised or team-created for this educational prototype; they are not official policy publications.</div>}
    </div>
  );
}

function decisionTitle(decision) {
  if (decision === "grounded") return "Grounded in approved sources";
  if (decision === "partial") return "Partially answerable";
  if (decision === "refuse-boundary") return "Outside the assistant’s scope";
  return "No supported answer found";
}

function CasesPage({ cases, onNavigate }) {
  const [filter, setFilter] = useState("all");
  const filtered = cases.filter((item) => filter === "all" || item.status.toLowerCase() === filter);
  return (
    <div className="page-content">
      <PageHeading eyebrow="YOUR RECORDS" title="My support cases" description="Review the cases associated with your demo profile. Case decisions and status changes are handled by staff." action={<button className="button button-primary" onClick={() => onNavigate("assistant")}><Plus size={16} /> Prepare a case</button>} />
      <div className="cases-summary-row">
        <div className="cases-summary-card"><span className="summary-square summary-blue"><FileCheck2 size={17} /></span><span><small>ALL CASES</small><strong>{cases.length}</strong></span></div>
        <div className="cases-summary-card"><span className="summary-square summary-amber"><Clock3 size={17} /></span><span><small>OPEN / PENDING</small><strong>{cases.filter((item) => ["pending", "in review"].includes(item.status.toLowerCase())).length}</strong></span></div>
        <div className="cases-summary-note"><ShieldCheck size={17} /><span>CampusIQ can prepare a draft. It cannot resolve, approve, or change the status of a case.</span></div>
      </div>
      <section className="surface-card cases-table-card">
        <div className="table-toolbar"><div><h2>Case records</h2><p>Your support request history.</p></div><div className="filter-tabs" role="group" aria-label="Filter cases">{["all", "pending", "in review", "resolved"].map((item) => <button className={filter === item ? "filter-active" : ""} onClick={() => setFilter(item)} key={item}>{item === "all" ? "All cases" : item}</button>)}</div></div>
        {filtered.length ? (
          <div className="table-scroll"><table className="data-table"><thead><tr><th>CASE</th><th>CATEGORY</th><th>SUMMARY</th><th>SUBMITTED</th><th>STATUS</th></tr></thead><tbody>
            {filtered.map((item) => <tr key={item.case_id}><td><span className="case-id-cell">{item.case_id}</span></td><td><span className="category-chip">{item.category.replaceAll("_", " ")}</span></td><td className="case-summary-cell">{item.description}</td><td>{formatDate(item.created_at)}</td><td><StatusBadge status={item.status} /></td></tr>)}
          </tbody></table></div>
        ) : <div className="empty-large"><span className="empty-icon"><FileCheck2 size={22} /></span><h3>{cases.length ? "No cases in this filter" : "Nothing here yet"}</h3><p>{cases.length ? "Try another status filter to see more case records." : "When you prepare and approve a support-case draft, it will appear here."}</p>{!cases.length && <button className="button button-primary" onClick={() => onNavigate("assistant")}>Ask CampusIQ to help <ArrowRight size={15} /></button>}</div>}
      </section>
      <div className="safe-data-note"><ShieldCheck size={16} /><span>Case details are shown only for the student ID in this demo session. Sample data is synthetic.</span></div>
    </div>
  );
}

function TimetablePage({ timetable }) {
  const entries = timetable?.entries || [];
  const daysOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const sortedEntries = [...entries].sort((a, b) => daysOrder.indexOf(a.day) - daysOrder.indexOf(b.day));
  return (
    <div className="page-content">
      <PageHeading eyebrow="YOUR STUDY PLAN" title="My timetable" description="A quick view of classes attached to your sample student profile." action={timetable && <span className="semester-pill"><CalendarDays size={15} />{timetable.semester}</span>} />
      <div className="timetable-info-banner"><span className="calendar-banner-icon"><CalendarDays size={18} /></span><span><strong>Semester timetable</strong><small>Showing the synthetic schedule associated with your demo profile.</small></span><span className="schedule-count">{entries.length} {entries.length === 1 ? "class" : "classes"}</span></div>
      {sortedEntries.length ? (
        <div className="timetable-list">{sortedEntries.map((item, index) => <article className="surface-card timetable-row" key={`${item.course_code}-${item.day}-${index}`}><div className="timetable-date-block"><span>{item.day.slice(0, 3).toUpperCase()}</span><strong>{item.day}</strong></div><div className="timetable-time"><Clock3 size={15} /><strong>{item.time}</strong></div><div className="timetable-course"><span className="course-code">{item.course_code}</span><span>{courseName(item.course_code)}</span></div><div className="timetable-location"><span className="location-pin"><ArrowDownRight size={14} /></span><span><small>LOCATION</small><strong>{item.room}</strong></span></div></article>)}</div>
      ) : <section className="surface-card empty-large timetable-empty"><span className="empty-icon"><CalendarDays size={22} /></span><h3>No timetable is available</h3><p>There is no timetable attached to this sample profile yet. Try another demo student or check the timetable data in this prototype.</p></section>}
      <div className="handbook-footnote"><Info size={14} /> Timetable records are sample data and may not reflect a current university schedule.</div>
    </div>
  );
}

function courseName(code) {
  const names = { BSE4104: "Emerging Trends in Software Engineering", BIT2207: "Web Technologies" };
  return names[code] || "Course";
}

function ChatsPage({ conversations, onOpen, onDelete, onClear, onNewChat }) {
  const [confirmClear, setConfirmClear] = useState(false);
  return (
    <div className="page-content">
      <PageHeading
        eyebrow="YOUR SAVED CONVERSATIONS"
        title="Chat history"
        description="Return to earlier conversations. They stay saved to your demo profile until you delete them."
        action={<div className="assistant-heading-actions">{conversations.length > 0 && <button className="button button-secondary" onClick={() => setConfirmClear(true)}><Trash2 size={15} /> Delete all</button>}<button className="button button-primary" onClick={onNewChat}><Plus size={15} /> New chat</button></div>}
      />
      {confirmClear && <div className="confirm-banner"><span><Info size={17} /> Delete all saved conversations for this demo profile?</span><div><button className="button button-quiet button-small" onClick={() => setConfirmClear(false)}>Cancel</button><button className="button button-danger button-small" onClick={async () => { await onClear(); setConfirmClear(false); }}>Delete all</button></div></div>}
      <section className="surface-card chats-card">
        <div className="table-toolbar"><div><h2>Conversations</h2><p>{conversations.length} saved {conversations.length === 1 ? "chat" : "chats"}</p></div><span className="history-retention"><ShieldCheck size={14} /> Private to this demo profile</span></div>
        {conversations.length ? (
          <div className="chat-history-list">
            {conversations.map((conversation) => (
              <article className="chat-history-row" key={conversation.id}>
                <button className="chat-history-open" onClick={() => onOpen(conversation.id)}>
                  <span className="history-search-icon"><MessageCircle size={17} /></span>
                  <span className="chat-history-copy"><strong>{conversation.title}</strong><small>{conversation.preview || "No messages yet"} · {new Date(conversation.updated_at).toLocaleString()}</small></span>
                  <ArrowRight size={16} />
                </button>
                <button className="icon-button chat-delete-button" onClick={() => onDelete(conversation.id)} aria-label={`Delete ${conversation.title}`} title="Delete conversation"><Trash2 size={15} /></button>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-large"><span className="empty-icon"><MessageCircle size={22} /></span><h3>No saved conversations yet</h3><p>Your chats will appear here automatically so you can return to them later.</p><button className="button button-primary" onClick={onNewChat}><Plus size={15} /> Start a conversation</button></div>
        )}
      </section>
      <div className="privacy-banner"><ShieldCheck size={17} /><span><strong>Saved on this app.</strong> Conversation messages and replies are stored in the local SQLite database until you delete them. This is a demo using sample student IDs, not secure authentication.</span></div>
    </div>
  );
}

function HistoryPage({ searches, onClear, onNavigate }) {
  const [confirmClear, setConfirmClear] = useState(false);
  return (
    <div className="page-content">
      <PageHeading eyebrow="YOUR SEARCH ACTIVITY" title="Search history" description="Your handbook searches, decisions, and cited documents. Assistant conversations are saved separately under Chat history." action={searches.length > 0 && <button className="button button-secondary" onClick={() => setConfirmClear(true)}><Trash2 size={15} /> Clear history</button>} />
      {confirmClear && <div className="confirm-banner"><span><Info size={17} /> Clear all saved handbook searches for this demo account?</span><div><button className="button button-quiet button-small" onClick={() => setConfirmClear(false)}>Cancel</button><button className="button button-danger button-small" onClick={async () => { await onClear(); setConfirmClear(false); }}>Clear searches</button></div></div>}
      <section className="surface-card history-card">
        <div className="table-toolbar"><div><h2>Handbook search activity</h2><p>{searches.length} {searches.length === 1 ? "search" : "searches"} saved</p></div><span className="history-retention"><ShieldCheck size={14} /> Private to this demo profile</span></div>
        {searches.length ? <div className="history-list">{searches.map((item) => (
          <article className="history-row" key={item.id}><span className="history-search-icon"><Search size={17} /></span><div className="history-main"><strong>{item.query}</strong><span>{new Date(item.created_at).toLocaleString()}</span></div><div className="history-sources">{item.sources.length ? item.sources.map((source) => <span className="citation-chip" key={source}>{source}</span>) : <span className="no-citation">No source cited</span>}</div><span className={`history-decision decision-label-${item.decision}`}>{decisionTitle(item.decision)}</span></article>
        ))}</div> : <div className="empty-large"><span className="empty-icon"><History size={22} /></span><h3>Your search history is empty</h3><p>When you search the approved handbook collection, the query, result type, and cited source IDs will appear here.</p><button className="button button-primary" onClick={() => onNavigate("handbook")}>Search the handbook <ArrowRight size={15} /></button></div>}
      </section>
      <div className="privacy-banner"><ShieldCheck size={17} /><span><strong>Search history and chats are separate.</strong> Handbook searches save their query and source metadata here; full chat transcripts appear in Chat history.</span></div>
    </div>
  );
}

function AboutPage({ onNavigate }) {
  return (
    <div className="page-content">
      <PageHeading eyebrow="A CLEARER WAY TO GET HELP" title="About CampusIQ" description="A student-support assistant designed to make approved guidance easier to find and everyday support tasks easier to navigate." />
      <section className="about-hero">
        <div className="about-brand-mark"><Sparkles size={29} /></div>
        <div className="about-hero-copy"><span className="hero-badge"><GraduationCap size={14} /> UNIVERSITY STUDENT SUPPORT</span><h2>Helpful guidance.<br />Human decisions.</h2><p>CampusIQ brings the project’s handbook search, case and timetable tools, and bounded support-case workflow into one friendly interface.</p></div>
        <div className="about-pill-list"><span><CheckCircle2 size={14} /> Source-grounded</span><span><CheckCircle2 size={14} /> Approval-first</span><span><CheckCircle2 size={14} /> Demo data</span></div>
      </section>
      <div className="about-card-grid">
        <section className="surface-card about-card"><span className="about-card-icon tone-blue"><BookOpen size={19} /></span><h3>Find approved guidance</h3><p>Search the project’s 12-document knowledge collection. Relevant answers include document references; if evidence is weak, the assistant may abstain.</p><button className="text-button" onClick={() => onNavigate("handbook")}>Explore the handbook <ArrowRight size={14} /></button></section>
        <section className="surface-card about-card"><span className="about-card-icon tone-teal"><CalendarDays size={19} /></span><h3>Check your own information</h3><p>Look up the timetable and case details linked to your selected synthetic student profile. Ownership checks stay in the existing tools.</p><button className="text-button" onClick={() => onNavigate("timetable")}>View timetable <ArrowRight size={14} /></button></section>
        <section className="surface-card about-card"><span className="about-card-icon tone-violet"><FileCheck2 size={19} /></span><h3>Prepare, then approve</h3><p>For supported case types, CampusIQ gathers details and presents an exact draft. A case is created only after you explicitly approve it.</p><button className="text-button" onClick={() => onNavigate("assistant")}>Ask CampusIQ <ArrowRight size={14} /></button></section>
      </div>
      <div className="about-boundaries">
        <div className="boundaries-heading"><span className="boundary-icon"><ShieldCheck size={19} /></span><div><h2>What CampusIQ does—and does not do</h2><p>Clear boundaries are part of how the system is designed.</p></div></div>
        <div className="boundary-columns"><div><span className="boundary-label boundary-yes"><Check size={13} /> CAN HELP WITH</span><ul><li>Handbook and course-outline questions grounded in the project corpus</li><li>Your own sample timetable and support-case lookups</li><li>Preparing a draft for missing marks, retakes, or registration issues</li><li>Showing where an answer came from or when it does not know</li></ul></div><div><span className="boundary-label boundary-no"><X size={13} /> DOES NOT</span><ul><li>Decide admissions, fee, grade, or disciplinary matters</li><li>Approve or resolve cases, or change a case’s status</li><li>Replace a department office or official university service</li><li>Authenticate a real student identity in this demo</li></ul></div></div>
      </div>
      <section className="data-transparency surface-card"><div className="transparency-icon"><Info size={18} /></div><div><h3>Data and prototype transparency</h3><p>Student, case and timetable records in this repository are intended to be synthetic. Handbook search metadata and assistant conversation transcripts are stored in local SQLite; conversations remain until the student deletes them. Case-workflow planning uses Gemini, while deterministic code enforces the action limits, permissions, and approval gate. Demo sign-in uses a student ID only and is <strong>not real authentication</strong>; never use real or sensitive student data with this prototype.</p></div></section>
    </div>
  );
}

export default App;
