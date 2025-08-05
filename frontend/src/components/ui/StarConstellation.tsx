'use client';

import React, { useEffect, useRef } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

interface Node {
  angle: number;
  distance: number;
  size: number;
  x: number;
  y: number;
  opacity: number;
}

const StarConstellation: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const animationRef = useRef<number>();
  const { isDarkMode } = useTheme();

  // Pan and zoom state
  const offset = useRef({ x: window.innerWidth * 0.25, y: 0 });
  const dragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const zoom = useRef(1);
  const targetZoom = useRef(1);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const createNodes = () => {
      const nodes: Node[] = [];
      const numNodes = 300;
      const radiusRange = 1000;

      for (let i = 0; i < numNodes; i++) {
        const angle = (Math.PI * 2 * i) / numNodes;
        const distance = Math.random() * radiusRange;

        nodes.push({
          angle,
          distance,
          size: Math.random() * 2 + 1,
          x: Math.cos(angle) * distance,
          y: Math.sin(angle) * distance,
          opacity: Math.random() * 0.5 + 0.5,
        });
      }

      nodesRef.current = nodes;
    };

    const draw = () => {
      const { width, height } = canvas;
      const centerX = width / 2 + offset.current.x;
      const centerY = height / 2 + offset.current.y;

      // Smooth zoom transition
      zoom.current += (targetZoom.current - zoom.current) * 0.1;

      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.scale(zoom.current, zoom.current);

      // Draw lines - Dark lines in light mode, white lines in dark mode
      const lineColor = isDarkMode
        ? 'rgba(255, 255, 255, 0.1)'
        : 'rgba(50, 50, 50, 0.15)';
      ctx.strokeStyle = lineColor;
      ctx.lineWidth = 1 / zoom.current;

      for (const node of nodesRef.current) {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(node.x, node.y);
        ctx.stroke();
      }

      // Draw nodes - Dark nodes in light mode, white nodes in dark mode
      for (const node of nodesRef.current) {
        const nodeColor = isDarkMode
          ? `rgba(255, 255, 255, ${node.opacity})`
          : `rgba(30, 30, 30, ${node.opacity})`;

        ctx.beginPath();
        ctx.fillStyle = nodeColor;
        ctx.arc(node.x, node.y, node.size / zoom.current, 0, Math.PI * 2);
        ctx.fill();
        
        // Add a subtle glow effect
        if (isDarkMode) {
          ctx.shadowColor = 'rgba(255, 255, 255, 0.3)';
          ctx.shadowBlur = 2;
        } else {
          ctx.shadowColor = 'rgba(30, 30, 30, 0.2)';
          ctx.shadowBlur = 1;
        }
        ctx.fill();
        ctx.shadowBlur = 0; // Reset shadow
      }

      ctx.restore();
    };

    const animate = () => {
      draw();
      animationRef.current = requestAnimationFrame(animate);
    };

    const onMouseDown = (e: MouseEvent) => {
      dragging.current = true;
      dragStart.current = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const dx = e.clientX - dragStart.current.x;
      const dy = e.clientY - dragStart.current.y;
      dragStart.current = { x: e.clientX, y: e.clientY };
      offset.current.x += dx;
      offset.current.y += dy;
    };

    const onMouseUp = () => {
      dragging.current = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = 0.05; // Reduced from 0.1 to 0.05
      if (e.deltaY < 0) {
        targetZoom.current *= 1 + zoomFactor;
      } else {
        targetZoom.current *= 1 - zoomFactor;
      }
      targetZoom.current = Math.max(0.5, Math.min(targetZoom.current, 2)); // Reduced zoom range
    };

    resizeCanvas();
    createNodes();
    animate();

    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('wheel', onWheel, { passive: false });

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('wheel', onWheel);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isDarkMode]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-auto cursor-grab active:cursor-grabbing"
      style={{ zIndex: 1 }}
    />
  );
};

export default StarConstellation;
