export default function SearchResults({ items, onDownload, onSelect, searching }) {
  if (searching) {
    return <p className="empty">Searching…</p>;
  }

  if (!items?.length) {
    return <p className="empty">No documents found.</p>;
  }

  return (
    <div className="results-grid" role="list">
      {items.map((item) => (
        <div key={item.id} className="result-item" role="listitem">
          <div>
            <div className="result-title">{item.filename}</div>
          </div>

          <div className="result-actions">
            <button className="result-btn" onClick={() => onDownload?.(item.id)}>
              Download
            </button>

            <button className="result-btn" onClick={() => onSelect?.(item)}>
              Chat
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}