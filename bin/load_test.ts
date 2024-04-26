#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { LoadTestStack } from '../lib/load_test_stack';

const app = new cdk.App();
new LoadTestStack(app, 'LoadTestStack', {
  env: {
    // AWS region to deploy this stack to. (Required for defining ALB access logging)
    region: 'eu-central-1',
    // Aws Account ID to deploy this stack to. (Also required only if you specify certificateArn below.)
    // account: '123456789012',
  },
  // Amazon Certificate Manager certificate ARN for Locust Web UI ALB.
  // ALB can be accessed with HTTP if you don't specify this argument.
  // certificateArn: "",

  // CIDRs that can access Locust Web UI ALB.
  // It is highly recommended to set this CIDR as narrowly as possible
  // when you do not enable the authentication option below.
  allowedCidrs: ['0.0.0.0/0'],

  // You can enable password auth for Locust web UI uncommenting lines below:
  webUsername: 'relocator',
  webPassword: 'RELOCAWS-398',

  // Any arbitrary command line options to pass to Locust.
  // An example would be:
  // Exclude Tags - List of tags to exclude from the test, so only tasks
  // with no matching tags will be executed.
  // additionalArguments: ['--exclude-tags', 'tag1', 'tag2'],
});
