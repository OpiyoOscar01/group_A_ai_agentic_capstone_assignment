import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

def draw_box(ax, x, y, w, h, text, color='#2196F3', fontsize=9, bold=False):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                         facecolor=color, edgecolor='#333333', linewidth=1.5)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color='white' if color != '#FFF9C4' else '#333')

def draw_arrow(ax, x1, y1, x2, y2, color='#666666'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=2))

# Title
ax.text(7, 9.6, 'RAG Architecture - University Student-Support Case Agent',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#1a237e')

# 1. Student Query (top)
draw_box(ax, 4.5, 8.7, 5, 0.6, 'STUDENT QUERY\n"What is the retake policy?"', '#5C6BC0', 10, True)
draw_arrow(ax, 7, 8.7, 7, 8.1)

# 2. Flask App (main container)
app_box = FancyBboxPatch((1.5, 4.5), 11, 3.4, boxstyle="round,pad=0.15",
                         facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=2)
ax.add_patch(app_box)
ax.text(7, 7.7, 'FLASK APPLICATION (app.py)', ha='center', va='center',
        fontsize=11, fontweight='bold', color='#1565C0')

# Steps inside Flask
draw_box(ax, 2, 6.5, 2, 0.7, '1. Receive\n   Query', '#42A5F5', 8)
draw_box(ax, 4.5, 6.5, 2, 0.7, '2. Extract\n   Intent', '#42A5F5', 8)
draw_box(ax, 7, 6.5, 2.5, 0.7, '3. RAG\n   Retrieval', '#FF9800', 8, True)
draw_box(ax, 10, 6.5, 2, 0.7, '4. Generate\n   Response', '#42A5F5', 8)

# Arrows between steps
draw_arrow(ax, 4, 6.85, 4.5, 6.85)
draw_arrow(ax, 6.5, 6.85, 7, 6.85)
draw_arrow(ax, 9.5, 6.85, 10, 6.85)

# Source citation box
draw_box(ax, 5, 5, 4, 0.8, '5. Add Source Citations\n   [Source: DOC-xx]', '#66BB6A', 8)
draw_arrow(ax, 7, 6.5, 7, 5.8)

# Response output
draw_box(ax, 10, 5, 2, 0.8, 'Response +\nSources', '#66BB6A', 8, True)
draw_arrow(ax, 9, 5.4, 10, 5.4)

# 3. RAG Pipeline (Oscar's module)
rag_box = FancyBboxPatch((0.5, 2.3), 5, 1.8, boxstyle="round,pad=0.1",
                         facecolor='#FFF3E0', edgecolor='#E65100', linewidth=2)
ax.add_patch(rag_box)
ax.text(3, 3.95, 'RAG RETRIEVAL MODULE', ha='center', va='center',
        fontsize=9, fontweight='bold', color='#E65100')

draw_box(ax, 0.7, 2.5, 1.3, 0.6, 'Ingest &\nChunk', '#FFB74D', 7)
draw_box(ax, 2.2, 2.5, 1.3, 0.6, 'Index\n(TF-IDF)', '#FFB74D', 7)
draw_box(ax, 3.7, 2.5, 1.5, 0.6, 'Top-k\nRetrieval', '#FF9800', 7, True)

draw_arrow(ax, 2, 2.8, 2.2, 2.8)
draw_arrow(ax, 3.5, 2.8, 3.7, 2.8)

# Arrow from Flask to RAG
draw_arrow(ax, 5, 6.5, 3.5, 4.1, '#E65100')
ax.text(3.8, 5.2, 'Query', fontsize=7, color='#E65100', ha='center')

# Arrow from RAG back to Flask
draw_arrow(ax, 4.5, 4.1, 8, 6.5, '#E65100')
ax.text(5.8, 5.2, 'Chunks + Sources', fontsize=7, color='#E65100', ha='center')

# 4. Gemini Model (right)
gemini_box = FancyBboxPatch((7.5, 2.3), 3, 1.8, boxstyle="round,pad=0.1",
                            facecolor='#E8F5E9', edgecolor='#2E7D32', linewidth=2)
ax.add_patch(gemini_box)
ax.text(9, 3.95, 'GEMINI MODEL', ha='center', va='center',
        fontsize=9, fontweight='bold', color='#2E7D32')

draw_box(ax, 7.7, 2.5, 1.2, 0.6, 'System\nPrompt', '#81C784', 7)
draw_box(ax, 9.1, 2.5, 1.2, 0.6, 'Generate\nAnswer', '#4CAF50', 7, True)

draw_arrow(ax, 8.9, 2.8, 9.1, 2.8)

# Arrow from Flask to Gemini
draw_arrow(ax, 11, 6.5, 9.5, 4.1, '#2E7D32')
ax.text(10.5, 5.2, 'Context + Query', fontsize=7, color='#2E7D32', ha='center')

# 5. Document Corpus (bottom)
corpus_box = FancyBboxPatch((0.5, 0.3), 13, 1.6, boxstyle="round,pad=0.1",
                            facecolor='#F3E5F5', edgecolor='#6A1B9A', linewidth=2)
ax.add_patch(corpus_box)
ax.text(7, 1.75, 'DOCUMENT CORPUS', ha='center', va='center',
        fontsize=10, fontweight='bold', color='#6A1B9A')

# Document boxes
docs = ['DOC-01\nAcademic\nRegulations', 'DOC-02\nStudent\nHandbook', 'DOC-03\nCourse\nSyllabus',
        'DOC-04\nFees\nStructure', 'DOC-xx\n...']
for i, doc in enumerate(docs):
    draw_box(ax, 1 + i*2.5, 0.5, 2, 0.9, doc, '#CE93D8', 7)

# Arrow from Corpus to RAG
draw_arrow(ax, 3, 2.3, 3, 2.1, '#6A1B9A')

# 6. Output (right side)
draw_box(ax, 11.5, 7, 2, 1, 'STUDENT\nRESPONSE', '#5C6BC0', 9, True)
draw_arrow(ax, 12, 7, 12, 7.5)

# Legend
legend_y = 0.1
ax.text(0.5, 9.9, 'Legend:', fontsize=8, fontweight='bold')
ax.add_patch(FancyBboxPatch((1.5, 9.75), 0.3, 0.15, boxstyle="round,pad=0.02", facecolor='#FF9800'))
ax.text(2, 9.83, 'RAG (Your Task)', fontsize=7)
ax.add_patch(FancyBboxPatch((4, 9.75), 0.3, 0.15, boxstyle="round,pad=0.02", facecolor='#42A5F5'))
ax.text(4.5, 9.83, 'Flask App', fontsize=7)
ax.add_patch(FancyBboxPatch((6.5, 9.75), 0.3, 0.15, boxstyle="round,pad=0.02", facecolor='#81C784'))
ax.text(7, 9.83, 'Gemini Model', fontsize=7)
ax.add_patch(FancyBboxPatch((9.5, 9.75), 0.3, 0.15, boxstyle="round,pad=0.02", facecolor='#CE93D8'))
ax.text(10, 9.83, 'Document Corpus', fontsize=7)

plt.tight_layout()
plt.savefig('D:/task/group_A_ai_agentic_capstone_assignment/docs/architecture/RAG_Architecture.png',
            dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
print('Diagram saved!')
