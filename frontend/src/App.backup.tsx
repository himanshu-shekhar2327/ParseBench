
import { useState } from 'react'
import {
  Activity, BarChart3, BookOpen, Check, ChevronDown, Clock3,
  Code2, Copy, FileText, FolderOpen, Gauge, History, Layers3,
  Menu, Play, Plus, Settings, ShieldCheck, UploadCloud, X,
} from 'lucide-react'

const API = 'http://127.0.0.1:8000'

const parsers = [
  { id: 'liteparse', name: 'LiteParse', detail: 'Fast local parsing', color: '#34d399' },
  { id: 'docling', name: 'Docling', detail: 'Document understanding', color: '#60a5fa' },
  { id: 'llamaparse', name: 'LlamaParse', detail: 'Cloud-based parsing', color: '#c084fc' },
  { id: 'azure', name: 'Azure DI', detail: 'OCR and extraction', color: '#fbbf24' },
]

const nav = [
  { name: 'Benchmark', icon: BarChart3 },
  { name: 'Runs history', icon: History },
  { name: 'Documents', icon: FolderOpen },
  { name: 'Parsers', icon: Layers3 },
]

type ParseResult = {
  status: string
  parser_id: string
  parser_name: string
  filename: string
  format: string
  input_bytes: number
  latency_seconds: number
  output_bytes: number
  output_characters: number
  output_markdown: string
  error?: string
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [parser, setParser] = useState('liteparse')
  const [documentType, setDocumentType] = useState('auto')
  const [outputFormat, setOutputFormat] = useState('markdown')
  const [result, setResult] = useState<ParseResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeNav, setActiveNav] = useState('Benchmark')
  const [dragging, setDragging] = useState(false)
  const [previewTab, setPreviewTab] = useState('output')
  const [mobileMenu, setMobileMenu] = useState(false)
  const [copied, setCopied] = useState(false)

  function selectFile(next: File | undefined) {
    if (!next) return
    setFile(next)
    setResult(null)
    setError('')
  }

  async function runParser() {
    if (!file) {
      setError('Choose a document before running the parser.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const body = new FormData()
      body.append('file', file)

      const response = await fetch(`${API}/api/parse/${parser}`, {
        method: 'POST',
        body,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Parsing failed. Check the backend logs.')
      }

      setResult(data as ParseResult)
    } catch (e) {
      setError(
        e instanceof Error
          ? `${e.message}. Ensure the FastAPI backend is running on port 8000.`
          : 'Unable to reach the parser API.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function copyOutput() {
    if (!result) return
    try {
      await navigator.clipboard.writeText(result.output_markdown)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1600)
    } catch {
      setError('Clipboard access failed. Select and copy the output manually.')
    }
  }

  const selectedParser = parsers.find((p) => p.id === parser)!

  return (
    <div className="min-h-screen bg-[#f5f7fb] text-slate-900">
      {mobileMenu && (
        <button
          aria-label="Close menu"
          className="fixed inset-0 z-30 bg-slate-950/40 lg:hidden"
          onClick={() => setMobileMenu(false)}
        />
      )}

      <aside className={`fixed inset-y-0 left-0 z-40 flex w-[248px] flex-col bg-[#111827] text-slate-300 transition-transform lg:translate-x-0 ${mobileMenu ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-[76px] items-center gap-3 border-b border-white/[0.08] px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500 text-white">
            <Activity size={21} />
          </div>
          <div>
            <div className="text-[17px] font-bold tracking-tight text-white">parsebench</div>
            <div className="text-[10px] tracking-[0.18em] text-slate-500">DOCUMENT INTELLIGENCE</div>
          </div>
        </div>

        <button className="mx-4 mt-5 flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.04] px-3 py-3 text-left">
          <span className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-400/15 text-indigo-300">
              <Layers3 size={17} />
            </div>
            <span>
              <span className="block text-xs font-semibold text-white">Parser workspace</span>
              <span className="mt-1 block text-[10px] text-slate-500">Personal workspace</span>
            </span>
          </span>
          <ChevronDown size={15} />
        </button>

        <div className="px-6 pb-2 pt-8 text-[10px] font-bold uppercase tracking-[0.17em] text-slate-500">
          WORKSPACE
        </div>
        <nav className="space-y-1 px-3">
          {nav.map(({ name, icon: Icon }) => (
            <button
              key={name}
              onClick={() => {
                setActiveNav(name)
                setMobileMenu(false)
              }}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-[13px] transition ${activeNav === name ? 'bg-indigo-500/15 font-semibold text-indigo-300' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
            >
              <Icon size={17} /> {name}
              {name === 'Runs history' && result && (
                <span className="ml-auto rounded-md bg-white/10 px-2 py-0.5 text-[10px]">1</span>
              )}
            </button>
          ))}
        </nav>

        <div className="px-6 pb-2 pt-8 text-[10px] font-bold uppercase tracking-[0.17em] text-slate-500">DEVELOPERS</div>
        <nav className="space-y-1 px-3">
          <button onClick={() => setActiveNav('Settings')} className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-[13px] ${activeNav === 'Settings' ? 'bg-indigo-500/15 text-indigo-300' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
            <Settings size={17} /> Settings
          </button>
          <button onClick={() => setActiveNav('API reference')} className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-[13px] ${activeNav === 'API reference' ? 'bg-indigo-500/15 text-indigo-300' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
            <Code2 size={17} /> API reference
          </button>
        </nav>

        <div className="mt-auto border-t border-white/[0.08] p-4">
          <div className="flex items-center gap-3 rounded-xl p-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-400 to-violet-600 text-xs font-bold text-white">PB</div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-semibold text-white">Parser Lab</div>
              <div className="mt-0.5 truncate text-[10px] text-slate-500">Local development</div>
            </div>
            <Settings size={15} className="text-slate-500" />
          </div>
        </div>
      </aside>

      <main className="min-h-screen lg:ml-[248px]">
        <header className="sticky top-0 z-20 flex h-[66px] items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-md sm:px-8">
          <div className="flex items-center gap-3">
            <button aria-label="Open navigation" onClick={() => setMobileMenu(true)} className="rounded-lg p-2 hover:bg-slate-100 lg:hidden">
              <Menu size={19} />
            </button>
            <div className="text-xs text-slate-400">Workspace <span className="mx-2">/</span> <span className="font-semibold text-slate-700">{activeNav}</span></div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-[11px] font-medium text-emerald-700 sm:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Local API
            </span>
            <button onClick={() => window.open(`${API}/docs`, '_blank')} className="hidden items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 sm:flex">
              <BookOpen size={15} /> API docs
            </button>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-[11px] font-bold text-indigo-700">PB</div>
          </div>
        </header>

        <div className="mx-auto max-w-[1440px] px-4 py-7 sm:px-8 sm:py-9">
          {activeNav === 'Benchmark' ? (
            <>
              <div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
                <div>
                  <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-indigo-700">
                    <Activity size={12} /> Document intelligence platform
                  </div>
                  <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-[34px]">Parser benchmark</h1>
                  <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">Evaluate document parsers side by side. Upload a file, choose a parser, and inspect its extracted content and real processing metrics.</p>
                </div>
                <button onClick={runParser} disabled={loading || !file} className="inline-flex items-center justify-center gap-2 self-start rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50 sm:self-auto">
                  {loading ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" /> : <Play size={15} fill="currentColor" />}
                  {loading ? 'Parsing document…' : 'Run parser'}
                </button>
              </div>

              <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_0.92fr]">
                <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-6">
                  <div className="mb-5 flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600"><UploadCloud size={20} /></div>
                      <div>
                        <h2 className="text-sm font-bold text-slate-900">Add documents</h2>
                        <p className="mt-1 text-xs text-slate-500">Upload a document to get started</p>
                      </div>
                    </div>
                    <span className="rounded-md bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-500">MAX 20 MB</span>
                  </div>

                  <label
                    onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={(e) => { e.preventDefault(); setDragging(false); selectFile(e.dataTransfer.files[0]) }}
                    className={`flex min-h-[205px] cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed px-5 py-8 text-center transition ${dragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 bg-slate-50/70 hover:border-indigo-400 hover:bg-indigo-50/40'}`}
                  >
                    <input type="file" className="hidden" accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.jpeg,.tif,.tiff,.webp,.bmp" onChange={(e) => selectFile(e.target.files?.[0])} />
                    <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200/80"><UploadCloud size={23} /></div>
                    <div className="text-sm font-semibold text-slate-800">{file ? file.name : 'Drop your file here, or browse'}</div>
                    <p className="mt-2 text-xs text-slate-500">{file ? `${formatBytes(file.size)} · Ready to parse` : 'PDF, DOCX, XLSX, PPTX, PNG, JPG and more'}</p>
                    <span className="mt-4 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700">Browse files</span>
                  </label>

                  {file && (
                    <div className="mt-3 flex items-center gap-3 rounded-xl border border-slate-200 px-3 py-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600"><FileText size={18} /></div>
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-xs font-semibold text-slate-800">{file.name}</div>
                        <div className="mt-1 text-[10px] text-slate-500">{formatBytes(file.size)}</div>
                      </div>
                      <button aria-label="Remove file" onClick={() => { setFile(null); setResult(null); setError('') }} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"><X size={16} /></button>
                    </div>
                  )}

                  <div className="mt-6 border-t border-slate-100 pt-5">
                    <div className="mb-3 text-xs font-bold text-slate-800">Document type</div>
                    <div className="relative">
                      <select value={documentType} onChange={(e) => setDocumentType(e.target.value)} className="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-3 pr-10 text-xs text-slate-700 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50">
                        <option value="auto">Auto-detect document type</option>
                        <option value="invoice">Invoice</option>
                        <option value="financial-report">Financial report</option>
                        <option value="contract">Contract</option>
                        <option value="research-paper">Research paper</option>
                        <option value="scanned-document">Scanned document</option>
                      </select>
                      <ChevronDown size={15} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    </div>
                    <p className="mt-2 text-[10px] text-slate-400">Classification is a UI setting; it is not yet sent to the parser API.</p>
                  </div>
                </section>

                <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-6">
                  <div className="mb-5 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-50 text-violet-600"><Layers3 size={20} /></div>
                    <div>
                      <h2 className="text-sm font-bold text-slate-900">Configure parser</h2>
                      <p className="mt-1 text-xs text-slate-500">Select the engine for this run</p>
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    {parsers.map((p) => (
                      <button key={p.id} onClick={() => { setParser(p.id); setResult(null); setError('') }} className={`flex w-full items-center gap-3 rounded-xl border p-3.5 text-left transition ${parser === p.id ? 'border-indigo-300 bg-indigo-50/70 ring-1 ring-indigo-100' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'}`}>
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg" style={{ backgroundColor: `${p.color}18`, color: p.color }}><Layers3 size={18} /></div>
                        <div className="min-w-0 flex-1">
                          <div className="text-xs font-bold text-slate-800">{p.name}</div>
                          <div className="mt-1 text-[10px] text-slate-500">{p.detail}</div>
                        </div>
                        <div className={`flex h-5 w-5 items-center justify-center rounded-full border ${parser === p.id ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-slate-300 text-transparent'}`}><Check size={12} /></div>
                      </button>
                    ))}
                  </div>

                  <div className="mt-5 border-t border-slate-100 pt-5">
                    <div className="mb-3 text-xs font-bold text-slate-800">Output format</div>
                    <div className="flex gap-2">
                      {['markdown', 'text'].map((fmt) => (
                        <button key={fmt} onClick={() => setOutputFormat(fmt)} className={`flex-1 rounded-lg border px-3 py-2.5 text-xs font-semibold capitalize transition ${outputFormat === fmt ? 'border-indigo-300 bg-indigo-50 text-indigo-700' : 'border-slate-200 text-slate-500 hover:bg-slate-50'}`}>{fmt}</button>
                      ))}
                    </div>
                    <div className="mt-4 flex items-center gap-3 rounded-xl bg-slate-50 p-3">
                      <ShieldCheck size={18} className="text-slate-500" />
                      <div className="flex-1">
                        <div className="text-xs font-semibold text-slate-700">Local processing</div>
                        <div className="mt-1 text-[10px] text-slate-500">Parser-specific execution and metrics</div>
                      </div>
                      <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    </div>
                    <p className="mt-3 text-[10px] leading-5 text-slate-400">Some parsers use cloud APIs. Your selected engine may send the document to its provider.</p>
                  </div>
                </section>
              </div>

              {error && (
                <div role="alert" className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  <X size={18} className="mt-0.5 shrink-0" />
                  <div className="flex-1">{error}</div>
                  <button aria-label="Dismiss error" onClick={() => setError('')}><X size={15} /></button>
                </div>
              )}

              {result ? (
                <>
                  <section className="mt-6 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-6">
                    <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                      <div>
                        <div className="flex items-center gap-2">
                          <h2 className="text-sm font-bold text-slate-900">Parsed output</h2>
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-semibold text-emerald-700"><Check size={11} /> Completed</span>
                        </div>
                        <p className="mt-1.5 text-xs text-slate-500">{result.filename} · {result.parser_name}</p>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={copyOutput} className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50">{copied ? <Check size={14} /> : <Copy size={14} />}{copied ? 'Copied' : 'Copy output'}</button>
                        <button onClick={() => {
                          const blob = new Blob([result.output_markdown], { type: 'text/markdown;charset=utf-8' })
                          const url = URL.createObjectURL(blob)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = `${result.filename}.md`
                          a.click()
                          URL.revokeObjectURL(url)
                        }} className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-700"><Plus size={14} /> Export .md</button>
                      </div>
                    </div>

                    <div className="mb-4 flex gap-5 border-b border-slate-200">
                      <button onClick={() => setPreviewTab('output')} className={`border-b-2 pb-3 text-xs font-semibold ${previewTab === 'output' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-slate-400'}`}>Parsed output</button>
                      <button onClick={() => setPreviewTab('preview')} className={`border-b-2 pb-3 text-xs font-semibold ${previewTab === 'preview' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-slate-400'}`}>Document preview</button>
                    </div>

                    {previewTab === 'output' ? (
                      <pre className="max-h-[430px] min-h-[200px] overflow-auto whitespace-pre-wrap rounded-xl bg-[#111827] p-5 font-mono text-xs leading-6 text-slate-200">{outputFormat === 'text' ? result.output_markdown.replace(/[#*_`]/g, '') : result.output_markdown}</pre>
                    ) : (
                      <div className="flex min-h-[200px] flex-col items-center justify-center rounded-xl border border-slate-200 bg-slate-50 p-8 text-center">
                        <FileText size={35} className="text-indigo-400" />
                        <p className="mt-3 text-sm font-semibold text-slate-800">{result.filename}</p>
                        <p className="mt-2 text-xs text-slate-500">Preview is not rendered in this version. The original file is available in your browser upload.</p>
                      </div>
                    )}
                  </section>

                  <section className="mt-6">
                    <div className="mb-4">
                      <h2 className="text-base font-bold text-slate-900">Performance metrics</h2>
                      <p className="mt-1 text-xs text-slate-500">Measured from the completed API run. Accuracy and confidence require a separate ground-truth evaluation.</p>
                    </div>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                      {[
                        { label: 'Processing time', value: `${result.latency_seconds.toFixed(2)}s`, note: 'End-to-end API timing', icon: Clock3, color: 'text-indigo-600', bg: 'bg-indigo-50' },
                        { label: 'Output size', value: formatBytes(result.output_bytes), note: `${result.output_characters.toLocaleString()} characters`, icon: FileText, color: 'text-emerald-600', bg: 'bg-emerald-50' },
                        { label: 'Input size', value: formatBytes(result.input_bytes), note: result.format.toUpperCase() + ' document', icon: Gauge, color: 'text-amber-600', bg: 'bg-amber-50' },
                        { label: 'Parser status', value: result.status === 'success' ? 'Success' : result.status, note: result.parser_name, icon: ShieldCheck, color: 'text-violet-600', bg: 'bg-violet-50' },
                      ].map((metric) => (
                        <div key={metric.label} className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-500">{metric.label}</span>
                            <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${metric.bg} ${metric.color}`}><metric.icon size={18} /></span>
                          </div>
                          <div className="mt-4 text-2xl font-bold tracking-tight text-slate-900">{metric.value}</div>
                          <div className="mt-2 text-[10px] text-slate-400">{metric.note}</div>
                        </div>
                      ))}
                    </div>

                    <div className="mt-5 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-6">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600"><BarChart3 size={20} /></div>
                        <div>
                          <h3 className="text-sm font-bold text-slate-900">Run summary</h3>
                          <p className="mt-1 text-xs text-slate-500">Actual measurements from this parser execution</p>
                        </div>
                      </div>
                      <div className="mt-5 grid grid-cols-1 gap-4 border-t border-slate-100 pt-5 sm:grid-cols-3">
                        <div><div className="text-[10px] uppercase tracking-wider text-slate-400">Selected parser</div><div className="mt-2 text-sm font-semibold text-slate-800">{selectedParser.name}</div></div>
                        <div><div className="text-[10px] uppercase tracking-wider text-slate-400">Document</div><div className="mt-2 break-all text-sm font-semibold text-slate-800">{result.filename}</div></div>
                        <div><div className="text-[10px] uppercase tracking-wider text-slate-400">Document type setting</div><div className="mt-2 text-sm font-semibold capitalize text-slate-800">{documentType.replaceAll('-', ' ')}</div></div>
                      </div>
                    </div>
                  </section>
                </>
              ) : (
                <section className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white/70 px-5 py-9 text-center">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-500"><Activity size={22} /></div>
                  <h2 className="mt-4 text-sm font-bold text-slate-800">Your results will appear here</h2>
                  <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-slate-500">Upload a document, choose one of the available parsers, and click Run parser. Results will include extracted content and measured performance metrics.</p>
                </section>
              )}
            </>
          ) : (
            <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm sm:p-12">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600"><Layers3 size={23} /></div>
              <h1 className="mt-5 text-2xl font-bold text-slate-900">{activeNav}</h1>
              <p className="mt-2 max-w-lg text-sm leading-6 text-slate-500">
                {activeNav === 'Runs history' ? 'Run history persistence is not implemented yet. The current result remains available in the Benchmark view.' :
                 activeNav === 'Documents' ? 'Document library and stored uploads are not implemented yet. Files are currently processed per request.' :
                 activeNav === 'Parsers' ? 'Available integrations: LiteParse, Docling, LlamaParse and Azure Document Intelligence. Select a parser from the Benchmark page to run it.' :
                 activeNav === 'API reference' ? 'Explore the FastAPI endpoints and test parser requests in the interactive API documentation.' :
                 'Workspace settings will be added in a future iteration.'}
              </p>
              {activeNav === 'API reference' ? (
                <button onClick={() => window.open(`${API}/docs`, '_blank')} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-700"><Code2 size={15} /> Open API documentation</button>
              ) : (
                <button onClick={() => setActiveNav('Benchmark')} className="mt-5 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-700">Back to benchmark</button>
              )}
            </section>
          )}

          <footer className="mt-10 flex flex-col justify-between gap-2 border-t border-slate-200 py-5 text-[10px] text-slate-400 sm:flex-row">
            <span>Parsebench · Document parser evaluation workspace</span>
            <span>Metrics are measured per run · Accuracy requires ground-truth validation</span>
          </footer>
        </div>
      </main>
    </div>
  )
}
