# Project Documentation Generator - Mermaid Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph UI ["🎨 Streamlit Web UI (app.py)"]
        Form["📝 Form Inputs<br/>- Project Title<br/>- Tech Stack<br/>- Summary<br/>- Code<br/>- Student Info"]
        Sidebar["📋 Sidebar<br/>- Test Mode<br/>- How it Works<br/>- Job History"]
        Results["✅ Results Display<br/>- Download Button<br/>- Tracking Details<br/>- Debug Logs"]
    end

    subgraph Pipeline ["⚙️ LangGraph Pipeline (pipeline.py)"]
        Node1["🔍 NODE 1<br/>analyze_input"]
        Node2["📝 NODE 2<br/>plan_document"]
        Node3["📄 NODE 3<br/>generate_front_matter"]
        Node4["📚 NODE 4<br/>generate_chapters"]
        Node5["🎯 NODE 5<br/>calibrate_content"]
        Node6["📖 NODE 6<br/>generate_references"]
        Node7["📋 NODE 7<br/>format_document"]
    end

    subgraph Modules ["🔧 Support Modules"]
        Config["⚙️ config.py<br/>All Constants"]
        Planner["📋 planner.py<br/>Document Plan"]
        Generator["✍️ content_generator.py<br/>Chapter Content"]
        Formatter["📄 doc_formatter.py<br/>Word Doc"]
        LLMClient["🤖 llm_client.py<br/>Azure OpenAI"]
        Tracker["📊 tracker.py<br/>Logs & Costs"]
    end

    subgraph External ["☁️ External Services"]
        Azure["Azure OpenAI API<br/>gpt-4.1-mini"]
        Storage["💾 Output Files<br/>output/<br/>tracking/"]
    end

    Form -->|Validate| Node1
    Sidebar -->|Test Data| Form
    Node1 -->|State| Node2
    Node2 -->|Plan| Node3
    Node3 -->|Front Matter| Node4
    Node4 -->|Chapters| Node5
    Node5 -->|Calibrated| Node6
    Node6 -->|References| Node7
    Node7 -->|Result| Results

    Node2 -.->|Uses| Planner
    Node3 -.->|Uses| Generator
    Node4 -.->|Uses| Generator
    Node5 -.->|Uses| Generator
    Node7 -.->|Uses| Formatter

    Planner -.->|LLM Call| LLMClient
    Generator -.->|LLM Call| LLMClient
    LLMClient -->|API Call| Azure
    LLMClient -->|Token Count| Config

    Node1 -.->|Track| Tracker
    Node2 -.->|Track| Tracker
    Node3 -.->|Track| Tracker
    Node4 -.->|Track| Tracker
    Node5 -.->|Track| Tracker
    Node6 -.->|Track| Tracker
    Node7 -.->|Track| Tracker

    Node7 -->|Save| Storage
    Tracker -->|Save JSON| Storage
    Results -->|Download| Storage
```

---

## 2. Pipeline Execution Flow (7-Node State Machine)

```mermaid
graph TD
    Start(["🚀 START"]) -->|Initialize State| Node1["<b>NODE 1: analyze_input</b><br/>─────────────<br/>✓ Validate inputs<br/>✓ Log metadata<br/>📊 Progress: 10%"]

    Node1 -->|PipelineState| Node2["<b>NODE 2: plan_document</b><br/>─────────────<br/>🤖 1 LLM Call<br/>📋 Output: Document Plan<br/>- Chapters<br/>- Page allocation<br/>- Word targets<br/>📊 Progress: 25%"]

    Node2 -->|document_plan| Node3["<b>NODE 3: generate_front_matter</b><br/>─────────────<br/>🤖 2 LLM Calls<br/>✓ Abstract 250-300 words<br/>✓ Acknowledgment 200-250<br/>📊 Progress: 35%"]

    Node3 -->|front_matter| Node4["<b>NODE 4: generate_chapters</b><br/>─────────────<br/>🤖 N LLM Calls Parallel<br/>⚡ Concurrency: 12<br/>✓ 1 call per chapter<br/>✓ Typical: 6-10 chapters<br/>📊 Progress: 70%"]

    Node4 -->|chapters_content| Node5["<b>NODE 5: calibrate_content</b><br/>─────────────<br/>📏 Check word count deviation<br/>⚠️ If deviation > 20%<br/>  → Re-generate chapter<br/>🤖 0-N LLM Calls (parallel)<br/>📊 Progress: 80%"]

    Node5 -->|calibrated_chapters| Node6["<b>NODE 6: generate_references</b><br/>─────────────<br/>🤖 1 LLM Call<br/>📚 Output: 15-25 References<br/>📋 Format: IEEE<br/>📊 Progress: 85%"]

    Node6 -->|references_content| Node7["<b>NODE 7: format_document</b><br/>─────────────<br/>📄 Assemble .docx file<br/>✓ Title page<br/>✓ Certificate<br/>✓ TOC, LOF, LOT<br/>✓ All chapters (parsed MD)<br/>✓ References<br/>✓ Appendix<br/>✓ Page numbers<br/>📊 Progress: 100%"]

    Node7 -->|output_file| End(["✅ END<br/>Return Result"])

    style Node1 fill:#e1f5e1
    style Node2 fill:#e3f2fd
    style Node3 fill:#f3e5f5
    style Node4 fill:#fff3e0
    style Node5 fill:#fce4ec
    style Node6 fill:#e0f2f1
    style Node7 fill:#f1f8e9
```

---

## 3. LLM Parallel Batch Processing (Node 4)

```mermaid
graph LR
    Start["🚀 Node 4 Start<br/>generate_chapters"]

    Start -->|Create Tasks| Queue["📋 Queue of LLM Calls<br/>─────────────<br/>Ch1: {prompt1}<br/>Ch2: {prompt2}<br/>Ch3: {prompt3}<br/>...<br/>Ch8: {prompt8}"]

    Queue -->|Semaphore: 12| Sem["⚙️ Async Semaphore<br/>Max 12 concurrent"]

    Sem -->|Release & Execute| Batch["🔄 Batch Execution (asyncio.gather)<br/>─────────────<br/>Call 1 → Azure API<br/>Call 2 → Azure API<br/>Call 3 → Azure API<br/>Call 4 → Azure API<br/>..."]

    Batch -->|Responses| Results["✅ Collect Results<br/>─────────────<br/>Ch1: {content, tokens}<br/>Ch2: {content, tokens}<br/>Ch3: {content, tokens}<br/>..."]

    Results -->|Track| Tracker["📊 Tracker<br/>Total tokens<br/>Total cost<br/>Per-chapter timing"]

    Tracker -->|Return| End["✅ chapters_content<br/>→ Node 5"]

    style Queue fill:#fff3e0
    style Sem fill:#ffccbc
    style Batch fill:#ffab91
    style Results fill:#ffccbc
    style Tracker fill:#ffccbc
```

---

## 4. Content Calibration Loop (Node 5)

```mermaid
graph TD
    Start["🚀 Node 5 Start<br/>calibrate_content"]

    Start -->|For Each Chapter| Check["📏 Check Word Count<br/>─────────────<br/>actual_words = ?<br/>target_words = ?<br/>deviation = |actual - target| / target"]

    Check -->|deviation <= 20%| Keep["✅ Keep As-Is<br/>Content acceptable"]

    Check -->|deviation > 20%| Below{"actual < target?"}

    Below -->|Yes| Expand["⬆️ EXPAND<br/>Re-generate with:<br/>- More examples<br/>- More explanations<br/>- Elaborate details"]

    Below -->|No| Condense["⬇️ CONDENSE<br/>Re-generate with:<br/>- Keep key points<br/>- Remove extra<br/>- Summarize"]

    Expand -->|LLM Call| Regen["🤖 Batch Regenerate<br/>All out-of-target chapters<br/>Parallel (Semaphore: 12)"]

    Condense -->|LLM Call| Regen

    Keep -->|Collect| End["✅ Calibrated Chapters<br/>→ Node 6"]

    Regen -->|Track| Tracker["📊 Tracker<br/>Calibration tokens<br/>Time spent"]

    Tracker -->|Collect| End

    style Check fill:#ffe0b2
    style Keep fill:#c8e6c9
    style Expand fill:#ffccbc
    style Condense fill:#ffccbc
    style Regen fill:#ff7043
```

---

## 5. Word Document Assembly (Node 7)

```mermaid
graph TD
    Start["🚀 Node 7 Start<br/>format_document"]

    Start -->|Init| DocInit["📋 DocumentFormatter<br/>─────────────<br/>✓ Create Document<br/>✓ Setup A4 page<br/>✓ Setup styles<br/>✓ Setup margins"]

    DocInit -->|Section 1| TitlePage["📑 add_title_page<br/>─────────────<br/>College Name<br/>Department<br/>Project Title<br/>Student Info<br/>Guide Name<br/>Year"]

    TitlePage -->|Section 2| CertPage["📜 add_certificate_page<br/>─────────────<br/>Formal Certificate<br/>Signature Table<br/>3 Sign Lines"]

    CertPage -->|Section 3| Ack["📝 add_acknowledgment<br/>─────────────<br/>LLM-generated (200-250 words)"]

    Ack -->|Section 4| Abs["📄 add_abstract<br/>─────────────<br/>LLM-generated (250-300 words)"]

    Abs -->|Section 5| TOC["📑 add_table_of_contents<br/>─────────────<br/>Word field code<br/>(auto-populate on update)"]

    TOC -->|Section 6| LOF["📊 add_list_of_figures<br/>─────────────<br/>Placeholder page"]

    LOF -->|Section 7| LOT["📊 add_list_of_tables<br/>─────────────<br/>Placeholder page"]

    LOT -->|Section 8| Chapters["📚 add_chapter N times<br/>─────────────<br/>For each chapter:<br/>✓ Parse markdown<br/>✓ Handle headings<br/>✓ Handle code blocks<br/>✓ Handle diagrams<br/>✓ Handle tables"]

    Chapters -->|Parse Content| Parse["🔍 _parse_and_add_content<br/>─────────────<br/>## Heading 2 → Heading 2 style<br/>### Heading 3 → Heading 3 style<br/>```code``` → Gray table<br/>[DIAGRAM] → Bordered box<br/>| table | → Word table<br/>**bold** → Bold run<br/>*italic* → Italic run"]

    Parse -->|Section 9| Refs["📖 add_references<br/>─────────────<br/>15-25 IEEE refs"]

    Refs -->|Section 10| Appendix["📎 add_appendix<br/>─────────────<br/>Source code<br/>First 10,000 chars"]

    Appendix -->|Footer| PageNum["🔢 add_page_numbers<br/>─────────────<br/>Insert PAGE field<br/>in footer"]

    PageNum -->|Save| Save["💾 save<br/>─────────────<br/>output/<br/>doc_YYYYMMDD_HHMMSS.docx"]

    Save -->|Return| End["✅ output_file path<br/>→ Node COMPLETE"]

    style DocInit fill:#e3f2fd
    style TitlePage fill:#f3e5f5
    style CertPage fill:#f3e5f5
    style Ack fill:#e8f5e9
    style Abs fill:#e8f5e9
    style TOC fill:#fff3e0
    style LOF fill:#fff3e0
    style LOT fill:#fff3e0
    style Chapters fill:#fce4ec
    style Parse fill:#ffccbc
    style Refs fill:#f1f8e9
    style Appendix fill:#f1f8e9
    style PageNum fill:#c8e6c9
    style Save fill:#81c784
```

---

## 6. LLM Client - Sync vs Async vs Batch

```mermaid
graph TD
    Start["🤖 LLM Client<br/>llm_client.py"]

    Start -->|Type A| CallLLM["call_llm<br/>─────────────<br/>🔄 Synchronous<br/>Used by:<br/>- Node 2<br/>- Node 6<br/>Single call<br/>Blocks until response"]

    Start -->|Type B| CallAsync["call_llm_async<br/>─────────────<br/>⚡ Asynchronous<br/>Used by:<br/>Async-compatible nodes<br/>Returns coroutine<br/>Non-blocking"]

    Start -->|Type C| BatchCall["batch_call_llm<br/>─────────────<br/>🔄⚡ Parallel Batch<br/>Used by:<br/>- Node 4<br/>- Node 5<br/>Multiple calls<br/>Semaphore gating"]

    CallLLM -->|Process| Flow1["1️⃣ Create LLM instance<br/>2️⃣ Format messages<br/>3️⃣ Invoke llm.invoke<br/>4️⃣ Count tokens<br/>5️⃣ Return {content, tokens}"]

    CallAsync -->|Process| Flow2["1️⃣ Create LLM instance<br/>2️⃣ Format messages<br/>3️⃣ Await llm.ainvoke<br/>4️⃣ Count tokens<br/>5️⃣ Return {content, tokens}"]

    BatchCall -->|Process| Flow3["1️⃣ Create list of tasks<br/>2️⃣ Create Semaphore(12)<br/>3️⃣ For each task:<br/>   - Acquire semaphore<br/>   - Call call_llm_async<br/>   - Release semaphore<br/>4️⃣ asyncio.gather all<br/>5️⃣ Return list"]

    Flow1 -->|API| Azure["Azure OpenAI<br/>gpt-4.1-mini"]
    Flow2 -->|API| Azure
    Flow3 -->|API| Azure

    Azure -->|Response| Token["🔢 count_tokens<br/>─────────────<br/>Use tiktoken<br/>Encode text<br/>Return token count"]

    Token -->|Track| Tracker["📊 tracker.py<br/>─────────────<br/>Log input tokens<br/>Log output tokens<br/>Calculate cost"]

    style CallLLM fill:#e3f2fd
    style CallAsync fill:#bbdefb
    style BatchCall fill:#90caf9
    style Flow1 fill:#64b5f6
    style Flow2 fill:#64b5f6
    style Flow3 fill:#64b5f6
    style Azure fill:#2196f3
    style Token fill:#ffd54f
    style Tracker fill:#81c784
```

---

## 7. Streamlit UI - User Interaction Flow

```mermaid
graph TD
    Start["🌐 Open http://localhost:8501"]

    Start -->|Page 1| Page1["📋 Initial Page<br/>─────────────<br/>Sidebar:<br/>- Test Mode Toggle<br/>- How it Works<br/>- Previous Jobs<br/><br/>Main:<br/>- Tab 1: Project Details<br/>- Tab 2: Student Info"]

    Page1 -->|Fill Form| Form["📝 Form Inputs<br/>─────────────<br/>Project Title*<br/>Tech Stack*<br/>Target Pages (slider)<br/>Summary (textarea)*<br/>Additional Info<br/>Code (paste/upload)<br/>College Format<br/>Student Name<br/>Roll Number<br/>College Name<br/>Department<br/>Guide Name<br/>Academic Year"]

    Form -->|Click Generate| Validate["✅ Validate<br/>─────────────<br/>Title non-empty?<br/>Summary non-empty?<br/>Tech stack non-empty?<br/>Summary >= 20 words?"]

    Validate -->|Validation Failed| Error["❌ Show Error<br/>─────────────<br/>Red alert box<br/>Error message<br/>Focus on field"]

    Error -->|Fix & Retry| Form

    Validate -->|Validation Passed| RunPipeline["🚀 Trigger Pipeline<br/>─────────────<br/>Save inputs in<br/>session_state<br/>Spawn background<br/>thread (daemon)<br/>Set generation_started=True<br/>Call st.rerun"]

    RunPipeline -->|Page 2| Page2["⏳ Generation In Progress<br/>─────────────<br/>Progress Bar<br/>(0% → 100%)<br/><br/>Debug Console<br/>(scrollable)<br/><br/>Live Log Output<br/>[  0.0s] 🚀 Pipeline started<br/>[  0.1s]    Job ID: doc_xxx<br/>[  3.2s] 📝 Planning...<br/>..."]

    Page2 -->|Poll Every 1s| Poll["🔄 Polling Loop<br/>─────────────<br/>get_progress():<br/>  - progress_pct<br/>  - current_step<br/>  - tokens<br/>  - cost<br/>get_logs():<br/>  - new log lines"]

    Poll -->|Update UI| Page2
    Page2 -->|Complete| Page3["✅ Results Page<br/>─────────────<br/>Green Success Banner<br/><br/>Status: Completed<br/>Total Tokens: XXXXX<br/>Cost: $X.XX<br/>Duration: X:XX<br/><br/>📥 Download Button<br/><br/>📊 Tracking Details<br/>   (Expandable)<br/>   - Full JSON<br/>   - Step breakdown<br/><br/>🔧 Debug Logs<br/>   (Expandable)<br/><br/>🔄 Generate Another"]

    Page3 -->|Click Download| Download["💾 Download<br/>─────────────<br/>output/doc_xxx.docx<br/>Browser download"]

    Page3 -->|Click Generate Another| Page1

    style Page1 fill:#e3f2fd
    style Form fill:#bbdefb
    style Validate fill:#81c784
    style Error fill:#ef5350
    style RunPipeline fill:#fdd835
    style Page2 fill:#fff9c4
    style Poll fill:#fff59d
    style Page3 fill:#c8e6c9
    style Download fill:#81c784
```

---

## 8. Async Threading Model

```mermaid
graph LR
    Start["🌀 Streamlit Event Loop"]

    Start -->|Initial| Render1["🎨 Render Page 1<br/>─────────────<br/>Form inputs<br/>Sidebar<br/>Test mode"]

    Render1 -->|User Click| Click["🖱️ Generate Button<br/>Click"]

    Click -->|Spawn Thread| Thread["🧵 Background Thread<br/>─────────────<br/>target: _run_pipeline<br/>daemon: True<br/>Args: user inputs<br/><br/>Main thread<br/>continues..."]

    Click -->|Rerun| Render2["🎨 Render Page 2<br/>─────────────<br/>Progress bar<br/>Debug console<br/>Placeholder"]

    Render2 -->|Poll Loop| PollLoop["🔄 Every 1s<br/>─────────────<br/>tracker.get_logs()<br/>tracker.get_progress()<br/>Update UI"]

    PollLoop -->|Repeat| PollLoop

    Thread -->|Executes| Pipeline["⚙️ run_pipeline<br/>─────────────<br/>nest_asyncio.apply()<br/>LangGraph compiles<br/>Execute 7 nodes<br/>Call LLM APIs<br/>Generate document<br/>Track progress"]

    Pipeline -->|Complete| Complete["✅ Set result<br/>session_state.result = result<br/>Call st.rerun"]

    Complete -->|Rerun| Render3["🎨 Render Page 3<br/>─────────────<br/>Results banner<br/>Download button<br/>Tracking details<br/>Debug logs"]

    PollLoop -->|Stop polling| Render3

    style Start fill:#e3f2fd
    style Render1 fill:#bbdefb
    style Render2 fill:#90caf9
    style Render3 fill:#64b5f6
    style Click fill:#fdd835
    style Thread fill:#ff9800
    style Pipeline fill:#ff7043
    style PollLoop fill:#fff59d
    style Complete fill:#81c784
```

---

## 9. Tracking & Cost Estimation

```mermaid
graph TD
    Start["📊 Tracking System<br/>tracker.py"]

    Start -->|Initialize| Init["🆕 ProcessTracker<br/>─────────────<br/>job_id<br/>start_time<br/>Empty logs[]<br/>Empty steps[]<br/>Empty errors[]"]

    Init -->|Node 1| N1["Node 1: analyze_input<br/>─────────────<br/>start_step()<br/>complete_step<br/>tokens: {in:0, out:0}<br/>duration: 0.01s"]

    N1 -->|Node 2| N2["Node 2: plan_document<br/>─────────────<br/>start_step()<br/>LLM Call<br/>input_tokens: 10K<br/>output_tokens: 4K<br/>duration: 5.2s<br/>complete_step()"]

    N2 -->|Node 3-7| Nodes["Node 3-7...<br/>─────────────<br/>Same pattern<br/>Track tokens<br/>Track timing<br/>Track LLM calls"]

    Nodes -->|Aggregate| Total["📈 Totals<br/>─────────────<br/>Total input: 127K<br/>Total output: 85K<br/>Total tokens: 212K<br/>Total LLM calls: 15<br/>Total duration: 186s"]

    Total -->|Calculate Cost| Cost["💰 Cost Estimation<br/>─────────────<br/>Input: 127K × $2.50/1M<br/>       = $0.3175<br/>Output: 85K × $10/1M<br/>        = $0.85<br/>TOTAL: ~$1.17<br/><br/>Pricing Model:<br/>GPT-4o Approximation"]

    Cost -->|Persist| JSON["💾 Save JSON<br/>─────────────<br/>tracking/<br/>doc_20260212_232509.json<br/><br/>{<br/>  job_id,<br/>  status,<br/>  steps[],<br/>  total_tokens,<br/>  cost_estimate_usd,<br/>  user_inputs,<br/>  document_plan,<br/>  errors[]<br/>}"]

    JSON -->|Display| UI["🎨 Show in UI<br/>─────────────<br/>Results banner<br/>Tracking details<br/>expandable"]

    style Init fill:#e8f5e9
    style N1 fill:#fff9c4
    style N2 fill:#ffe0b2
    style Nodes fill:#ffccbc
    style Total fill:#b2dfdb
    style Cost fill:#c8e6c9
    style JSON fill:#d1c4e9
    style UI fill:#bbdefb
```

---

## 10. Complete End-to-End Flow

```mermaid
graph TD
    A["👤 User Opens App<br/>http://localhost:8501"]

    B["📋 Streamlit UI Renders<br/>Form + Sidebar"]

    C{["Enable Test Mode?"]}

    D["🧪 Auto-fill<br/>Sample Data"]

    E["📝 User Fills Form<br/>Project Details<br/>Student Info"]

    C -->|Yes| D
    C -->|No| E
    D --> F
    E --> F

    F["🖱️ Click Generate<br/>Button"]

    G["✅ Validate Inputs<br/>Non-empty check<br/>Word count check"]

    H{["Valid?"]}

    I["❌ Show Error<br/>Highlight field"]

    H -->|No| I
    I -->|Fix| F
    H -->|Yes| J

    J["🚀 Spawn Background Thread<br/>Trigger st.rerun"]

    K["⏳ Page 2: Progress Display<br/>Progress bar<br/>Debug console"]

    L["⚙️ LangGraph Pipeline<br/>7-Node State Machine<br/>Starting..."]

    M["🔄 Poll Loop<br/>Every 1 second<br/>Update UI"]

    N["🤖 Node 1-2: Planning<br/>Analyze input<br/>Plan document"]

    O["📄 Node 3: Front Matter<br/>Generate Abstract<br/>Generate Acknowledgment"]

    P["📚 Node 4: Chapters<br/>Parallel batch (12)<br/>Generate all chapters"]

    Q["🎯 Node 5: Calibration<br/>Check word counts<br/>Re-generate if needed"]

    R["📖 Node 6: References<br/>Generate IEEE refs"]

    S["📋 Node 7: Format<br/>Assemble .docx<br/>Parse markdown"]

    T["✅ Pipeline Complete<br/>Return result<br/>Trigger st.rerun"]

    U["✅ Page 3: Results<br/>Success banner<br/>Download button<br/>Tracking details<br/>Debug logs"]

    V["💾 Download .docx<br/>output/doc_xxx.docx"]

    W["✔️ Success<br/>Open in Word<br/>Update TOC<br/>Edit as needed"]

    A --> B
    B --> C
    F --> G
    G --> H
    J --> K
    K --> L
    L --> M
    L --> N
    N --> O
    O --> P
    P --> Q
    Q --> R
    R --> S
    S --> T
    M -->|Poll| M
    T --> U
    U --> V
    V --> W

    style A fill:#e3f2fd
    style B fill:#bbdefb
    style D fill:#fff9c4
    style E fill:#f3e5f5
    style F fill:#fdd835
    style G fill:#c8e6c9
    style H fill:#81c784
    style I fill:#ef5350
    style J fill:#ff9800
    style K fill:#ffe0b2
    style L fill:#ff7043
    style M fill:#fff59d
    style N fill:#ffccbc
    style O fill:#f8bbd0
    style P fill:#f48fb1
    style Q fill:#ec407a
    style R fill:#e91e63
    style S fill:#c2185b
    style T fill:#81c784
    style U fill:#c8e6c9
    style V fill:#a5d6a7
    style W fill:#66bb6a
```

