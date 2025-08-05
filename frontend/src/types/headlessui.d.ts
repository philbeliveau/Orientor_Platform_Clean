declare module '@headlessui/react' {
  import { ComponentType, ReactNode } from 'react';

  interface DisclosureProps {
    children: (props: { open: boolean }) => ReactNode;
    defaultOpen?: boolean;
    as?: ComponentType<any>;
  }

  export const Disclosure: ComponentType<DisclosureProps>;
  export const DisclosureButton: ComponentType<any>;
  export const DisclosurePanel: ComponentType<any>;
} 