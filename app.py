import streamlit as st
import PyPDF2
import os
import tempfile
from pathlib import Path
import base64
from datetime import datetime
from streamlit_option_menu import option_menu

# 页面配置
st.set_page_config(
    page_title="PDF页面提取工具",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #F0FDF4;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #F59E0B;
        margin-bottom: 1rem;
    }
    .stButton button {
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #2563EB;
    }
    .page-preview {
        background-color: #F8FAFC;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #E2E8F0;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 创建必要的目录
for dir_name in ['uploads', 'extracted']:
    os.makedirs(dir_name, exist_ok=True)

def extract_pdf_pages(input_path, output_path, pages_to_extract):
    """
    从PDF中提取指定页面
    """
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            total_pages = len(reader.pages)
            extracted_pages = []
            
            for page_num in pages_to_extract:
                index = page_num - 1
                if 0 <= index < total_pages:
                    page = reader.pages[index]
                    writer.add_page(page)
                    extracted_pages.append(page_num)
                else:
                    st.warning(f"第 {page_num} 页不存在，PDF共有 {total_pages} 页")
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True, extracted_pages, total_pages
    except Exception as e:
        return False, str(e), 0

def parse_page_input(page_str, max_pages):
    """
    解析页面输入字符串
    """
    pages = []
    if not page_str:
        return pages
    
    # 替换中文逗号，分割不同的部分
    parts = page_str.replace('，', ',').split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if '-' in part:
            # 处理范围
            try:
                if part.startswith('-'):
                    # 如 "-5" 表示从第1页到第5页
                    end = int(part[1:])
                    start = 1
                elif part.endswith('-'):
                    # 如 "5-" 表示从第5页到最后一页
                    start = int(part[:-1])
                    end = max_pages
                else:
                    # 正常范围 "5-10"
                    range_parts = part.split('-')
                    start = int(range_parts[0])
                    end = int(range_parts[1])
                
                # 确保范围有效
                start = max(1, start)
                end = min(max_pages, end)
                
                if start <= end:
                    pages.extend(range(start, end + 1))
            except ValueError:
                st.warning(f"忽略无效范围: {part}")
        else:
            # 处理单个页面
            try:
                page = int(part)
                if 1 <= page <= max_pages:
                    pages.append(page)
            except ValueError:
                st.warning(f"忽略无效页码: {part}")
    
    # 去重并排序
    return sorted(set(pages))

def get_pdf_preview(pdf_path, max_pages=10):
    """
    获取PDF的预览信息
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            preview_info = {
                'total_pages': total_pages,
                'pages': []
            }
            
            # 只预览前几页，避免性能问题
            for i in range(min(total_pages, max_pages)):
                page = reader.pages[i]
                text = page.extract_text()[:200]  # 只取前200个字符
                preview_info['pages'].append({
                    'page_number': i + 1,
                    'preview': text.strip() or f"第 {i+1} 页 (无文本或为图片)"
                })
            
            return preview_info
    except Exception as e:
        return None

def get_download_link(file_path, link_text):
    """
    生成文件下载链接
    """
    with open(file_path, "rb") as f:
        data = f.read()
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
    return href

# 侧边栏导航
with st.sidebar:
    st.title("📄 PDF工具")
    
    selected = option_menu(
        menu_title="功能菜单",
        options=["提取页面", "批量提取", "使用说明"],
        icons=["scissors", "files", "info-circle"],
        menu_icon="menu-app",
        default_index=0,
    )

# 主标题
st.markdown('<h1 class="main-header">📄 PDF页面提取工具</h1>', unsafe_allow_html=True)

if selected == "提取页面":
    st.markdown('<div class="info-box">上传PDF文件，选择需要提取的页面，生成新的PDF文件。</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="sub-header">📤 上传PDF文件</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("选择PDF文件", type=['pdf'], key="single_file")
        
        if uploaded_file is not None:
            # 保存上传的文件
            temp_dir = tempfile.gettempdir()
            input_path = os.path.join('uploads', uploaded_file.name)
            
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"文件上传成功: {uploaded_file.name}")
            
            # 显示PDF信息
            preview_info = get_pdf_preview(input_path)
            if preview_info:
                st.info(f"📊 PDF总页数: {preview_info['total_pages']} 页")
                
                # 显示预览
                with st.expander("📖 查看页面预览"):
                    for page_info in preview_info['pages']:
                        st.markdown(f"""
                        <div class="page-preview">
                        <strong>第 {page_info['page_number']} 页:</strong><br>
                        {page_info['preview']}
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="sub-header">⚙️ 设置提取参数</div>', unsafe_allow_html=True)
                
                if preview_info:
                    total_pages = preview_info['total_pages']
                    
                    # 页面选择方式
                    selection_method = st.radio(
                        "选择方式",
                        ["手动输入", "范围选择", "选择奇数页", "选择偶数页"]
                    )
                    
                    pages_to_extract = []
                    
                    if selection_method == "手动输入":
                        page_input = st.text_input(
                            "输入要提取的页面",
                            placeholder="例如: 1,3,5 或 1-5 或 1,3,5-10",
                            help="支持逗号分隔和连字符范围"
                        )
                        if page_input:
                            pages_to_extract = parse_page_input(page_input, total_pages)
                    
                    elif selection_method == "范围选择":
                        start_page = st.number_input("起始页", min_value=1, max_value=total_pages, value=1)
                        end_page = st.number_input("结束页", min_value=1, max_value=total_pages, value=total_pages)
                        
                        if start_page <= end_page:
                            pages_to_extract = list(range(start_page, end_page + 1))
                        else:
                            st.error("起始页不能大于结束页")
                    
                    elif selection_method == "选择奇数页":
                        pages_to_extract = [i for i in range(1, total_pages + 1) if i % 2 == 1]
                    
                    elif selection_method == "选择偶数页":
                        pages_to_extract = [i for i in range(1, total_pages + 1) if i % 2 == 0]
                    
                    # 显示选中的页面
                    if pages_to_extract:
                        st.info(f"✅ 已选择 {len(pages_to_extract)} 页: {pages_to_extract}")
                        
                        # 提取按钮
                        if st.button("🚀 开始提取页面", type="primary"):
                            with st.spinner("正在提取页面..."):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                output_filename = f"extracted_{timestamp}.pdf"
                                output_path = os.path.join('extracted', output_filename)
                                
                                success, result, total = extract_pdf_pages(input_path, output_path, pages_to_extract)
                                
                                if success:
                                    st.markdown('<div class="success-box">✅ 页面提取成功！</div>', unsafe_allow_html=True)
                                    
                                    # 显示提取结果
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.metric("原PDF页数", total)
                                    with col_b:
                                        st.metric("提取页数", len(result))
                                    
                                    # 提供下载
                                    st.markdown("### 📥 下载提取的文件")
                                    with open(output_path, "rb") as f:
                                        st.download_button(
                                            label="下载提取的PDF",
                                            data=f,
                                            file_name=output_filename,
                                            mime="application/pdf"
                                        )
                                    
                                    # 预览提取的文件
                                    with st.expander("👁️ 预览提取的PDF"):
                                        extracted_preview = get_pdf_preview(output_path)
                                        if extracted_preview:
                                            for page_info in extracted_preview['pages']:
                                                st.markdown(f"""
                                                <div class="page-preview">
                                                <strong>第 {page_info['page_number']} 页:</strong><br>
                                                {page_info['preview']}
                                                </div>
                                                """, unsafe_allow_html=True)
                                else:
                                    st.error(f"提取失败: {result}")
                    else:
                        st.warning("请选择要提取的页面")

elif selected == "批量提取":
    st.markdown('<div class="sub-header">📚 批量提取多个PDF文件</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">可以同时上传多个PDF文件，为每个文件设置提取的页面。</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "选择多个PDF文件", 
        type=['pdf'], 
        accept_multiple_files=True,
        key="batch_files"
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
        
        # 为每个文件设置提取参数
        extraction_tasks = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            with st.expander(f"文件 {i+1}: {uploaded_file.name}", expanded=i==0):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**文件名:** {uploaded_file.name}")
                    
                    # 保存临时文件
                    temp_path = os.path.join('uploads', f"temp_{i}_{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 获取PDF信息
                    preview = get_pdf_preview(temp_path)
                    if preview:
                        st.info(f"总页数: {preview['total_pages']}")
                        
                        # 页面选择
                        page_input = st.text_input(
                            f"提取页面 ({uploaded_file.name})",
                            key=f"pages_{i}",
                            placeholder="例如: 1,3,5 或 1-5",
                            help="输入要提取的页面"
                        )
                        
                        if page_input and preview:
                            pages = parse_page_input(page_input, preview['total_pages'])
                            if pages:
                                st.success(f"将提取 {len(pages)} 页: {pages}")
                                extraction_tasks.append({
                                    'input_path': temp_path,
                                    'original_name': uploaded_file.name,
                                    'pages': pages,
                                    'total_pages': preview['total_pages']
                                })
                
                with col2:
                    if preview and preview['pages']:
                        st.write("**第一页预览:**")
                        st.text(preview['pages'][0]['preview'][:100] + "...")
        
        # 批量处理按钮
        if extraction_tasks and st.button("🚀 批量处理所有文件", type="primary"):
            progress_bar = st.progress(0)
            results = []
            
            for idx, task in enumerate(extraction_tasks):
                progress = (idx + 1) / len(extraction_tasks)
                progress_bar.progress(progress)
                
                output_filename = f"extracted_{task['original_name']}"
                output_path = os.path.join('extracted', output_filename)
                
                success, result, total = extract_pdf_pages(
                    task['input_path'], 
                    output_path, 
                    task['pages']
                )
                
                if success:
                    results.append({
                        'filename': task['original_name'],
                        'output_path': output_path,
                        'extracted_pages': len(result),
                        'total_pages': total
                    })
            
            progress_bar.empty()
            
            # 显示批量处理结果
            st.markdown('<div class="success-box">✅ 批量处理完成！</div>', unsafe_allow_html=True)
            
            for result in results:
                with st.expander(f"📄 {result['filename']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("原文件页数", result['total_pages'])
                    with col2:
                        st.metric("提取页数", result['extracted_pages'])
                    
                    # 下载按钮
                    with open(result['output_path'], "rb") as f:
                        st.download_button(
                            label=f"下载 {result['filename']}",
                            data=f,
                            file_name=f"extracted_{result['filename']}",
                            mime="application/pdf",
                            key=f"download_{result['filename']}"
                        )

elif selected == "使用说明":
    st.markdown('<div class="sub-header">📖 使用说明</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 功能简介
    
    PDF页面提取工具可以帮助你从PDF文件中提取指定的页面，生成新的PDF文件。
    
    ### 📝 页面选择格式
    
    支持多种页面选择格式：
    
    1. **单个页面**：`3`（提取第3页）
    2. **多个页面**：`1,3,5`（提取第1,3,5页）
    3. **页面范围**：`1-5`（提取第1到5页）
    4. **组合格式**：`1,3,5-8,10`（提取第1,3,5,6,7,8,10页）
    5. **特殊格式**：
       - `-5`：从第1页到第5页
       - `5-`：从第5页到最后一页
    
    ### 🔄 处理流程
    
    1. 上传PDF文件
    2. 选择要提取的页面
    3. 点击"提取页面"按钮
    4. 下载提取后的PDF文件
    
    ### ⚠️ 注意事项
    
    - 提取的页面数量不能超过原PDF的总页数
    - 大型PDF文件处理可能需要一些时间
    - 提取后的文件会暂时保存在服务器，请及时下载
    
    ### 🛠️ 技术特性
    
    - 使用PyPDF2库进行PDF处理
    - 支持批量文件处理
    - 提供页面预览功能
    - 实时显示处理进度
    """)
    
    st.markdown('<div class="warning-box">⚠️ 注意：本工具不会永久保存您的文件，所有上传的文件在处理后会定期清理。</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "PDF页面提取工具 © 2024 | 使用 PyPDF2 和 Streamlit 构建"
    "</div>",
    unsafe_allow_html=True
)