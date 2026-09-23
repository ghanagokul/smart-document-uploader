import UploadArea from "./components/UploadArea";
import JobCard from "./components/JobCard";
import SearchBar from "./components/SearchBar";
import SearchResults from "./components/SearchResults";
import ChatPanel from "./components/ChatPanel";

import { useJobs } from "./state/useJobs";
import { useSearch } from "./state/useSearch";
import { useChat } from "./state/useChat";
import { getResult } from "./api/ocr.api";

export default function MainApp({ onLogout }) {
  const { jobs, addJob } = useJobs();
  const { results, searching, handleSearch } = useSearch();
  const {
    selectedDoc,
    chatMessages,
    chatInput,
    chatLoading,
    setChatInput,
    openChatForDoc,
    closeChat,
    sendQuestion,
  } = useChat();

  const handleDownload = async (documentId) => {
    const result = await getResult(documentId);
    if (!result?.url) {
      console.error("Failed to get download URL");
      return;
    }

    const link = document.createElement("a");
    link.href = result.url;
    link.download = result.filename || "document";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container">
      <header>
        <h1>Smart OCR & Tagging</h1>
        <p>
          Upload documents, search them, download results, and chat with content.
        </p>
        <button type="button" onClick={onLogout}>
          Log out
        </button>
      </header>

      <UploadArea onNewJob={addJob} />
      <SearchBar onSearch={handleSearch} />

      <SearchResults
        items={results}
        searching={searching}
        onSelect={openChatForDoc}
        onDownload={handleDownload}
      />

      <section className="jobs">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </section>

      {selectedDoc && (
        <ChatPanel
          selectedDoc={selectedDoc}
          chatMessages={chatMessages}
          chatInput={chatInput}
          chatLoading={chatLoading}
          setChatInput={setChatInput}
          handleSendQuestion={sendQuestion}
          onClose={closeChat}
        />
      )}
    </div>
  );
}