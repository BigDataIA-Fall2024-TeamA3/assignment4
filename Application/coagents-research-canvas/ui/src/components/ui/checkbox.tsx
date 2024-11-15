// src/components/ui/checkbox.tsx

import React from 'react';

type CheckboxProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Checkbox: React.FC<CheckboxProps> = (props) => {
  return <input type="checkbox" {...props} />;
};
