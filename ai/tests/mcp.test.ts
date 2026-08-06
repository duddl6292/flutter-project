import assert from 'node:assert/strict';
import test from 'node:test';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

import { createMcpHttpServer } from '../src/mcp/server.js';
import {
  getAccessiblePatientClinicalSummaryInputSchema,
} from '../src/mcp/tools/getAccessiblePatientClinicalSummary.js';
import {
  getAccessiblePatientExaminationsInputSchema,
} from '../src/mcp/tools/getAccessiblePatientExaminations.js';
import {
  getAccessiblePatientPrescriptionsInputSchema,
} from '../src/mcp/tools/getAccessiblePatientPrescriptions.js';
import {
  getAccessibleCTAnalysisResultsInputSchema,
} from '../src/mcp/tools/getAccessibleCTAnalysisResults.js';
import {
  getClinicianWorkSummaryInputSchema,
} from '../src/mcp/tools/getClinicianWorkSummary.js';
import {
  getMyAppointmentsInputSchema,
} from '../src/mcp/tools/getMyAppointments.js';
import {
  getMyMedicationPlanInputSchema,
} from '../src/mcp/tools/getMyMedicationPlan.js';
import {
  getMyMedicalHistoryInputSchema,
  getMyNotificationsInputSchema,
  getMyPrescriptionsInputSchema,
  getMyReleasedCTResultsInputSchema,
  getMyReleasedTestResultsInputSchema,
} from '../src/mcp/tools/patientRecordTools.js';
import {
  searchAccessibleConsultationsInputSchema,
} from '../src/mcp/tools/searchAccessibleConsultations.js';
import {
  getAccessiblePatientAppointmentsInputSchema,
  getAccessiblePatientAppointmentsOutputSchema,
} from '../src/mcp/tools/getAccessiblePatientAppointments.js';
import {
  backendStatusInputSchema,
  backendStatusOutputSchema,
} from '../src/mcp/tools/getBackendStatus.js';
import {
  systemStatusInputSchema,
  systemStatusOutputSchema,
} from '../src/mcp/tools/getSystemStatus.js';
import {
  searchAccessiblePatientsInputSchema,
  searchAccessiblePatientsOutputSchema,
} from '../src/mcp/tools/searchAccessiblePatients.js';
import {
  searchHospitalsInputSchema,
  searchHospitalsOutputSchema,
} from '../src/mcp/tools/searchHospitals.js';

test('mock tool schemas accept only the documented status shape', () => {
  assert.deepEqual(systemStatusInputSchema.parse({}), {});
  assert.deepEqual(
    systemStatusOutputSchema.parse({
      status: 'ok',
      service: 'brainon-mcp',
      database_access: false,
    }),
    {
      status: 'ok',
      service: 'brainon-mcp',
      database_access: false,
    },
  );
});

test('backend status schemas accept only the documented health shape', () => {
  assert.deepEqual(backendStatusInputSchema.parse({}), {});
  assert.deepEqual(
    backendStatusOutputSchema.parse({
      status: 'ok',
      service: 'brainon-backend',
      reachable: true,
    }),
    {
      status: 'ok',
      service: 'brainon-backend',
      reachable: true,
    },
  );
});

test('hospital search schemas accept the documented result shape', () => {
  assert.deepEqual(searchHospitalsInputSchema.parse({}), {
    search: '',
    limit: 5,
  });
  assert.deepEqual(
    searchHospitalsOutputSchema.parse({
      hospitals: [
        {
          hospital_id: '11111111-1111-4111-8111-111111111111',
          hospital_code: 'H001',
          hospital_name: 'BrainOn Hospital',
          address: 'Seoul',
          phone: '02-0000-0000',
        },
      ],
      meta: {
        page: 1,
        page_size: 10,
        total_count: 1,
        total_pages: 1,
      },
    }).hospitals[0]?.hospital_code,
    'H001',
  );
});

test('accessible patient search schemas expose only minimal authorized data', () => {
  assert.deepEqual(searchAccessiblePatientsInputSchema.parse({}), {
    search: '',
    limit: 5,
  });
  const result = searchAccessiblePatientsOutputSchema.parse({
    patients: [
      {
        patient_id: '22222222-2222-4222-8222-222222222222',
        medical_record_number: 'MRN-SYNTHETIC-001',
        name: 'Synthetic Patient',
        birth_date: '1990-01-01',
        sex: 'M',
        status: 'ACTIVE',
        access_scope: 'HOSPITAL',
        shared_consultation_id: null,
        access_expires_at: null,
      },
    ],
    meta: {
      page: 1,
      page_size: 5,
      total_count: 1,
      total_pages: 1,
    },
  });
  assert.equal(result.patients[0]?.access_scope, 'HOSPITAL');
  assert.equal('phone' in result.patients[0]!, false);
});

test('accessible appointment schemas accept patient appointment data', () => {
  assert.equal(
    getAccessiblePatientAppointmentsInputSchema.parse({
      patient_id: '44444444-4444-4444-8444-444444444444',
    }).patient_id,
    '44444444-4444-4444-8444-444444444444',
  );
  const result = getAccessiblePatientAppointmentsOutputSchema.parse({
    appointments: [
      {
        appointment_id: '55555555-5555-4555-8555-555555555555',
        patient_id: '44444444-4444-4444-8444-444444444444',
        patient_name: 'Synthetic Patient',
        clinician_id: '66666666-6666-4666-8666-666666666666',
        clinician_name: 'Synthetic Clinician',
        department_code: 'NEURO',
        department_name: 'Neurology',
        hospital_id: null,
        hospital_name: null,
        scheduled_at: '2026-08-07T10:00:00+09:00',
        duration_minutes: 30,
        location: 'Room 1',
        status: 'SCHEDULED',
      },
    ],
    meta: { total_count: 1 },
  });
  assert.equal(result.appointments[0]?.duration_minutes, 30);
});

test('clinician read tool inputs require scoped identifiers and safe defaults', () => {
  const patientId = '77777777-7777-4777-8777-777777777777';
  assert.equal(
    getAccessiblePatientClinicalSummaryInputSchema.parse({
      patient_id: patientId,
    }).patient_id,
    patientId,
  );
  assert.equal(
    getAccessiblePatientExaminationsInputSchema.parse({
      patient_id: patientId,
    }).limit,
    5,
  );
  assert.equal(
    getAccessiblePatientPrescriptionsInputSchema.parse({
      patient_id: patientId,
    }).limit,
    5,
  );
  assert.equal(
    getAccessibleCTAnalysisResultsInputSchema.parse({
      patient_id: patientId,
    }).limit,
    5,
  );
  assert.equal(searchAccessibleConsultationsInputSchema.parse({}).box, 'all');
  assert.deepEqual(getClinicianWorkSummaryInputSchema.parse({}), {});
});

test('patient self-service read tools use safe defaults without patient ids', () => {
  assert.deepEqual(getMyMedicationPlanInputSchema.parse({}), {
    remaining_only: false,
  });
  assert.deepEqual(getMyAppointmentsInputSchema.parse({}), {
    upcoming_only: true,
    limit: 10,
  });
  assert.equal(getMyReleasedTestResultsInputSchema.parse({}).limit, 10);
  assert.equal(getMyPrescriptionsInputSchema.parse({}).limit, 10);
  assert.equal(getMyMedicalHistoryInputSchema.parse({}).limit, 10);
  assert.equal(getMyReleasedCTResultsInputSchema.parse({}).limit, 10);
  assert.equal(getMyNotificationsInputSchema.parse({}).limit, 10);
});

test('sequential MCP clients can discover the non-medical status tool', async () => {
  const started = await createMcpHttpServer(0, '127.0.0.1');
  try {
    for (let attempt = 0; attempt < 2; attempt += 1) {
      const client = new Client(
        { name: `brainon-mcp-test-${attempt}`, version: '0.1.0' },
      );
      try {
        await client.connect(
          new StreamableHTTPClientTransport(
            new URL(`http://127.0.0.1:${started.port}/mcp`),
          ),
        );
        const tools = await client.listTools();
        assert.ok(
          tools.tools.some((tool) => tool.name === 'getSystemStatus'),
        );
        assert.ok(
          tools.tools.some((tool) => tool.name === 'getBackendStatus'),
        );
        assert.ok(
          tools.tools.some((tool) => tool.name === 'searchHospitals'),
        );
        assert.ok(
          tools.tools.some(
            (tool) => tool.name === 'searchAccessiblePatients',
          ),
        );
        assert.ok(
          tools.tools.some(
            (tool) => tool.name === 'getAccessiblePatientAppointments',
          ),
        );
        for (const toolName of [
          'getAccessiblePatientClinicalSummary',
          'getAccessiblePatientExaminations',
          'getAccessiblePatientPrescriptions',
          'getAccessibleCTAnalysisResults',
          'getClinicianWorkSummary',
          'searchAccessibleConsultations',
          'getMyMedicationPlan',
          'getMyAppointments',
          'getMyReleasedTestResults',
          'getMyPrescriptions',
          'getMyMedicalHistory',
          'getMyReleasedCTResults',
          'getMyNotifications',
        ]) {
          assert.ok(
            tools.tools.some((tool) => tool.name === toolName),
            `${toolName} should be discoverable`,
          );
        }
      } finally {
        await client.close();
      }
    }
  } finally {
    await started.close();
  }
});

test('patient tool forwards the MCP session token to Django', async () => {
  const originalFetch = globalThis.fetch;
  let forwardedAuthorization: string | null = null;
  globalThis.fetch = async (input, init) => {
    const url = input instanceof Request ? input.url : String(input);
    if (url.includes('/api/v1/patients/')) {
      forwardedAuthorization = new Headers(init?.headers).get('Authorization');
      return new Response(JSON.stringify({
        data: [
          {
            patient_id: '33333333-3333-4333-8333-333333333333',
            medical_record_number: 'MRN-SYNTHETIC-002',
            name: 'Authorized Synthetic Patient',
            birth_date: '1985-02-03',
            sex: 'F',
            phone: '010-0000-0000',
            status: 'ACTIVE',
            access_scope: 'HOSPITAL',
            shared_consultation_id: null,
            access_expires_at: null,
          },
        ],
        meta: {
          page: 1,
          page_size: 5,
          total_count: 1,
          total_pages: 1,
        },
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return originalFetch(input, init);
  };

  const started = await createMcpHttpServer(0, '127.0.0.1');
  const client = new Client(
    { name: 'brainon-auth-test', version: '0.1.0' },
  );
  try {
    await client.connect(
      new StreamableHTTPClientTransport(
        new URL(`http://127.0.0.1:${started.port}/mcp`),
        {
          requestInit: {
            headers: { 'X-BrainOn-User-Token': 'synthetic-access-token' },
          },
        },
      ),
    );
    const result = await client.callTool({
      name: 'searchAccessiblePatients',
      arguments: { search: 'Synthetic', limit: 5 },
    });
    assert.equal(result.isError, undefined);
    assert.equal(forwardedAuthorization, 'Bearer synthetic-access-token');
  } finally {
    await client.close();
    await started.close();
    globalThis.fetch = originalFetch;
  }
});
