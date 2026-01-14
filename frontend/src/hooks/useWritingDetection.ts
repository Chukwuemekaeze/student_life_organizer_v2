// src/hooks/useWritingDetection.ts
import { useEffect, useRef } from 'react';
import { setUserWriting } from './useAutoRefresh';

interface UseWritingDetectionOptions {
  // Delay before considering user as "actively writing" (ms)
  startDelay?: number;
  // Delay before considering user has "stopped writing" (ms) 
  stopDelay?: number;
  // Whether to enable detection
  enabled?: boolean;
}

export function useWritingDetection(
  elementRef: React.RefObject<HTMLElement>,
  options: UseWritingDetectionOptions = {}
) {
  const {
    startDelay = 100,    // Start detecting writing after 100ms of activity
    stopDelay = 1000,    // Stop detecting writing after 1s of inactivity
    enabled = true
  } = options;

  const isWritingRef = useRef(false);
  const startTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const stopTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled || !elementRef.current) return;

    const element = elementRef.current;

    const handleInput = () => {
      // Clear any existing stop timeout
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
        stopTimeoutRef.current = null;
      }

      // If not already writing, start the writing detection after a small delay
      if (!isWritingRef.current) {
        if (startTimeoutRef.current) {
          clearTimeout(startTimeoutRef.current);
        }
        
        startTimeoutRef.current = setTimeout(() => {
          isWritingRef.current = true;
          setUserWriting(true);
        }, startDelay);
      }

      // Set stop timeout
      stopTimeoutRef.current = setTimeout(() => {
        isWritingRef.current = false;
        setUserWriting(false);
      }, stopDelay);
    };

    const handleFocus = () => {
      // User focused on input - might start writing
      handleInput();
    };

    const handleBlur = () => {
      // User left the input - stop writing detection quickly
      if (startTimeoutRef.current) {
        clearTimeout(startTimeoutRef.current);
        startTimeoutRef.current = null;
      }
      
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
        stopTimeoutRef.current = null;
      }

      // Immediate stop
      setTimeout(() => {
        isWritingRef.current = false;
        setUserWriting(false);
      }, 200); // Small delay to handle quick focus changes
    };

    // Add event listeners for various input types
    element.addEventListener('input', handleInput);
    element.addEventListener('keydown', handleInput);
    element.addEventListener('focus', handleFocus);
    element.addEventListener('blur', handleBlur);

    // For contenteditable elements
    if (element.isContentEditable) {
      element.addEventListener('beforeinput', handleInput);
    }

    // Cleanup
    return () => {
      element.removeEventListener('input', handleInput);
      element.removeEventListener('keydown', handleInput);
      element.removeEventListener('focus', handleFocus);
      element.removeEventListener('blur', handleBlur);
      
      if (element.isContentEditable) {
        element.removeEventListener('beforeinput', handleInput);
      }

      // Clear timeouts
      if (startTimeoutRef.current) {
        clearTimeout(startTimeoutRef.current);
      }
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
      }

      // Reset writing state
      isWritingRef.current = false;
      setUserWriting(false);
    };
  }, [enabled, elementRef, startDelay, stopDelay]);

  return {
    isWriting: isWritingRef.current
  };
}

// Hook for form containers - detects writing in any input within the container
export function useFormWritingDetection(
  containerRef: React.RefObject<HTMLElement>,
  options: UseWritingDetectionOptions = {}
) {
  const { enabled = true, startDelay = 100, stopDelay = 1000 } = options;
  const isWritingRef = useRef(false);
  const stopTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled || !containerRef.current) return;

    const container = containerRef.current;

    const handleInputActivity = () => {
      // Clear any existing stop timeout
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
        stopTimeoutRef.current = null;
      }

      // Mark as writing
      if (!isWritingRef.current) {
        isWritingRef.current = true;
        setUserWriting(true);
      }

      // Set stop timeout
      stopTimeoutRef.current = setTimeout(() => {
        isWritingRef.current = false;
        setUserWriting(false);
      }, stopDelay);
    };

    const handleFocusIn = (e: Event) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        handleInputActivity();
      }
    };

    const handleFocusOut = () => {
      // Quick timeout to handle focus changes between inputs
      setTimeout(() => {
        const activeElement = document.activeElement as HTMLElement;
        const isStillInForm = container.contains(activeElement) && 
                             (activeElement.tagName === 'INPUT' || 
                              activeElement.tagName === 'TEXTAREA' || 
                              activeElement.isContentEditable);
        
        if (!isStillInForm) {
          if (stopTimeoutRef.current) {
            clearTimeout(stopTimeoutRef.current);
          }
          isWritingRef.current = false;
          setUserWriting(false);
        }
      }, 200);
    };

    // Listen for focus events on the container
    container.addEventListener('focusin', handleFocusIn);
    container.addEventListener('focusout', handleFocusOut);
    container.addEventListener('input', handleInputActivity);
    container.addEventListener('keydown', handleInputActivity);

    return () => {
      container.removeEventListener('focusin', handleFocusIn);
      container.removeEventListener('focusout', handleFocusOut); 
      container.removeEventListener('input', handleInputActivity);
      container.removeEventListener('keydown', handleInputActivity);

      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
      }

      isWritingRef.current = false;
      setUserWriting(false);
    };
  }, [enabled, containerRef, startDelay, stopDelay]);

  return {
    isWriting: isWritingRef.current
  };
}




