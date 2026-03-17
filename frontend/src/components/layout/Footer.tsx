export default function Footer() {
  return (
    <footer className="mt-auto bg-gray-800 text-white">
      <div className="mx-auto max-w-7xl px-4 py-6 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} LAKDA — LLM-Assisted Knowledge Discovery Application
      </div>
    </footer>
  );
}
