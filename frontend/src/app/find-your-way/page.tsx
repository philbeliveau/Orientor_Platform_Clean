'use client';

import React from 'react';
import { Container } from '@mui/material';
import FindYourWay from '@/components/FindYourWay';
import MainLayout from '@/components/layout/MainLayout';

export default function FindYourWayPage() {
  return (
    <MainLayout>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <FindYourWay />
      </Container>
    </MainLayout>
  );
} 