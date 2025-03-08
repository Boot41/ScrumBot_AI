import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BotIcon, UserIcon } from '../ChatIcons';

describe('ChatIcons Components', () => {
  test('renders BotIcon with correct classes', () => {
    const { container } = render(<BotIcon />);
    
    // Check container
    const iconContainer = container.querySelector('.icon-container');
    expect(iconContainer).toBeInTheDocument();
    
    // Check rings
    const rings = container.querySelectorAll('.ring.bot');
    expect(rings).toHaveLength(2);
    
    // Check core and text
    const core = container.querySelector('.icon-core.bot');
    expect(core).toBeInTheDocument();
    const text = container.querySelector('.icon-text.bot');
    expect(text).toBeInTheDocument();
    expect(text).toHaveTextContent('AI');
  });

  test('renders UserIcon with correct classes', () => {
    const { container } = render(<UserIcon />);
    
    // Check container
    const iconContainer = container.querySelector('.icon-container');
    expect(iconContainer).toBeInTheDocument();
    
    // Check rings
    const rings = container.querySelectorAll('.ring.user');
    expect(rings).toHaveLength(2);
    
    // Check core and text
    const core = container.querySelector('.icon-core.user');
    expect(core).toBeInTheDocument();
    const text = container.querySelector('.icon-text.user');
    expect(text).toBeInTheDocument();
    expect(text).toHaveTextContent('You');
  });

  test('BotIcon rings have correct animation delays', () => {
    const { container } = render(<BotIcon />);
    
    const rings = container.querySelectorAll('.ring.bot');
    const delays = Array.from(rings).map(ring => 
      (ring as HTMLElement).style.animationDelay
    );
    
    expect(delays).toEqual(['0s', '-1s']);
  });

  test('UserIcon rings have correct animation delays', () => {
    const { container } = render(<UserIcon />);
    
    const rings = container.querySelectorAll('.ring.user');
    const delays = Array.from(rings).map(ring => 
      (ring as HTMLElement).style.animationDelay
    );
    
    expect(delays).toEqual(['0s', '-1s']);
  });
});
