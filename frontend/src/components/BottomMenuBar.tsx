import { JSX } from 'react';
import '../styles/BottomMenuBar.css';

export function BottomMenuBar(): JSX.Element {
    return (
        <div className='bottom-menu-bar-component'>
            <div className='keyboard-shortcuts-image-container'>
                <button>
                    <svg xmlns='http://www.w3.org/2000/svg' height='24px' viewBox='0 -960 960 960' width='24px' fill='#FFFFFF'><path d='M160-200q-33 0-56.5-23.5T80-280v-400q0-33 23.5-56.5T160-760h640q33 0 56.5 23.5T880-680v400q0 33-23.5 56.5T800-200H160Zm0-80h640v-400H160v400Zm160-40h320v-80H320v80ZM200-440h80v-80h-80v80Zm120 0h80v-80h-80v80Zm120 0h80v-80h-80v80Zm120 0h80v-80h-80v80Zm120 0h80v-80h-80v80ZM200-560h80v-80h-80v80Zm120 0h80v-80h-80v80Zm120 0h80v-80h-80v80Zm120 0h80v-80h-80v80Zm120 0h80v-80h-80v80ZM160-280v-400 400Z'/></svg>
                    <div className='keyboard-shortcuts-window-popup'>
                        <h3>Keyboard Shortcuts</h3>
                        <p><span className='shortcut-key'>F11</span>Full Screen (Recommended)</p>
                    </div>
                </button>
            </div>
        </div>
    )
}
