// Tiptap Editor with Tailwind CSS styling
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';

function initializeTiptapEditor(textareaId) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) {
        console.error(`Textarea with id "${textareaId}" not found`);
        return null;
    }

    // Create editor container
    const editorContainer = document.createElement('div');
    editorContainer.className = 'tiptap-editor-wrapper border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden';
    textarea.parentNode.insertBefore(editorContainer, textarea);
    textarea.style.display = 'none';

    // Create toolbar
    const toolbar = document.createElement('div');
    toolbar.className = 'tiptap-toolbar flex flex-wrap items-center gap-2 p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800';
    editorContainer.appendChild(toolbar);

    // Create editor content area
    const editorContent = document.createElement('div');
    editorContent.className = 'tiptap-editor-content min-h-[400px] p-4 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100';
    editorContainer.appendChild(editorContent);

    // Create editor
    const editor = new Editor({
        element: editorContent,
        extensions: [
            StarterKit.configure({
                heading: {
                    levels: [1, 2, 3],
                },
            }),
            Placeholder.configure({
                placeholder: 'Start writing your blog post...',
            }),
        ],
        content: textarea.value || '',
        editorProps: {
            attributes: {
                class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-xl dark:prose-invert max-w-none focus:outline-none min-h-[400px]',
            },
        },
        onUpdate: ({ editor }) => {
            textarea.value = editor.getHTML();
        },
    });

    // Create toolbar buttons
    const buttonConfigs = [
        {
            name: 'bold',
            icon: '<strong>B</strong>',
            title: 'Bold',
            action: () => editor.chain().focus().toggleBold().run(),
            isActive: () => editor.isActive('bold'),
        },
        {
            name: 'italic',
            icon: '<em>I</em>',
            title: 'Italic',
            action: () => editor.chain().focus().toggleItalic().run(),
            isActive: () => editor.isActive('italic'),
        },
        {
            name: 'strike',
            icon: '<s>S</s>',
            title: 'Strikethrough',
            action: () => editor.chain().focus().toggleStrike().run(),
            isActive: () => editor.isActive('strike'),
        },
        { type: 'separator' },
        {
            name: 'heading1',
            icon: 'H1',
            title: 'Heading 1',
            action: () => editor.chain().focus().toggleHeading({ level: 1 }).run(),
            isActive: () => editor.isActive('heading', { level: 1 }),
        },
        {
            name: 'heading2',
            icon: 'H2',
            title: 'Heading 2',
            action: () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
            isActive: () => editor.isActive('heading', { level: 2 }),
        },
        {
            name: 'heading3',
            icon: 'H3',
            title: 'Heading 3',
            action: () => editor.chain().focus().toggleHeading({ level: 3 }).run(),
            isActive: () => editor.isActive('heading', { level: 3 }),
        },
        { type: 'separator' },
        {
            name: 'bulletList',
            icon: '• List',
            title: 'Bullet List',
            action: () => editor.chain().focus().toggleBulletList().run(),
            isActive: () => editor.isActive('bulletList'),
        },
        {
            name: 'orderedList',
            icon: '1. List',
            title: 'Numbered List',
            action: () => editor.chain().focus().toggleOrderedList().run(),
            isActive: () => editor.isActive('orderedList'),
        },
        {
            name: 'blockquote',
            icon: '"',
            title: 'Blockquote',
            action: () => editor.chain().focus().toggleBlockquote().run(),
            isActive: () => editor.isActive('blockquote'),
        },
        { type: 'separator' },
        {
            name: 'code',
            icon: '</>',
            title: 'Inline Code',
            action: () => editor.chain().focus().toggleCode().run(),
            isActive: () => editor.isActive('code'),
        },
        {
            name: 'codeBlock',
            icon: '{ }',
            title: 'Code Block',
            action: () => editor.chain().focus().toggleCodeBlock().run(),
            isActive: () => editor.isActive('codeBlock'),
        },
        { type: 'separator' },
        {
            name: 'undo',
            icon: '↶',
            title: 'Undo',
            action: () => editor.chain().focus().undo().run(),
            isDisabled: () => !editor.can().undo(),
        },
        {
            name: 'redo',
            icon: '↷',
            title: 'Redo',
            action: () => editor.chain().focus().redo().run(),
            isDisabled: () => !editor.can().redo(),
        },
    ];

    const buttons = [];

    buttonConfigs.forEach((config) => {
        if (config.type === 'separator') {
            const separator = document.createElement('div');
            separator.className = 'w-px h-6 bg-gray-300 dark:bg-gray-600';
            toolbar.appendChild(separator);
        } else {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `tiptap-button px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                config.isActive && config.isActive()
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            } ${config.isDisabled && config.isDisabled() ? 'opacity-50 cursor-not-allowed' : ''}`;
            button.title = config.title;
            button.innerHTML = config.icon;
            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (config.isDisabled && config.isDisabled()) return;
                config.action();
                updateToolbar();
            });
            toolbar.appendChild(button);
            buttons.push({ button, config });
        }
    });

    function updateToolbar() {
        buttons.forEach(({ button, config }) => {
            if (config.isActive) {
                if (config.isActive()) {
                    button.className = `tiptap-button px-3 py-1.5 rounded text-sm font-medium transition-colors bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300`;
                } else {
                    button.className = `tiptap-button px-3 py-1.5 rounded text-sm font-medium transition-colors text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700`;
                }
            }
            if (config.isDisabled) {
                if (config.isDisabled()) {
                    button.classList.add('opacity-50', 'cursor-not-allowed');
                } else {
                    button.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            }
        });
    }

    // Update toolbar on editor update
    editor.on('update', updateToolbar);
    editor.on('selectionUpdate', updateToolbar);

    // Update textarea on form submit
    const form = textarea.closest('form');
    if (form) {
        form.addEventListener('submit', () => {
            textarea.value = editor.getHTML();
        });
    }

    return editor;
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.initializeTiptapEditor = initializeTiptapEditor;
}

// Auto-initialize editors on page load
document.addEventListener('DOMContentLoaded', () => {
    // List of textarea IDs that should use the rich text editor
    const editorTextareas = [
        'id_content',           // BlogPostForm, NoteForm
        'content',              // JournalEntryForm (custom form, uses id="content")
        'id_description',       // TutorialForm
        'id_executive_summary', // BusinessPlanForm
    ];
    
    editorTextareas.forEach(textareaId => {
        const textarea = document.getElementById(textareaId);
        if (textarea) {
            // Only initialize if textarea doesn't have data-no-editor attribute
            if (!textarea.hasAttribute('data-no-editor')) {
                initializeTiptapEditor(textareaId);
            }
        }
    });
});
