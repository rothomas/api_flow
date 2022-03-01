import api_flow
import argparse
import os
import sys


parser = argparse.ArgumentParser(
    description='api-flow: an API chaining tool',
    prog='api_flow'
)
parser.add_argument(
    'flow_name',
    metavar='flow',
    type=str,
    help='basename of the YAML file containing a flow definition'
)
paths = parser.add_argument_group('data paths', 'Customize the data file locations for api-flow')
paths.add_argument(
    '--data-path',
    dest='data_path',
    type=str,
    metavar='DIR',
    help='a directory containing flow configuration data (default: current directory)'
)
paths.add_argument(
    '--flow-path',
    dest='flow_path',
    type=str,
    metavar='DIR',
    help='a directory containing flow definitions (default: <data-path>/flows)'
)
paths.add_argument(
    '--function-path',
    dest='function_path',
    type=str,
    metavar='DIR',
    help='a python module exposing user-defined template-substitution functions (default: <data-path>/functions)'
)
paths.add_argument(
    '--profile-path',
    dest='profile_path',
    type=str,
    metavar='DIR',
    help='a directory containing profile YAML files (default: <data-path>/profiles)'
)
paths.add_argument(
    '--template-path',
    dest='template_path',
    type=str,
    metavar='DIR',
    help='a directory containing template files (default: <data_path>/templates)'
)
parser.add_argument(
    '--profile',
    action='append',
    type=str,
    metavar='PROFILE',
    help='basename of a profile YAML file to include (multiple --profile flags are allowed)'
)


args = parser.parse_args()

api_flow.configure(
    data_path=args.data_path,
    flow_path=args.flow_path,
    function_path=args.function_path,
    profile_path=args.profile_path,
    template_path=args.template_path
)
print('DATA PATHS:', file=sys.stderr)
print(f'     Base: {api_flow.Config.data_path}', file=sys.stderr)
print(f'    Flows: {api_flow.Config.flow_path}', file=sys.stderr)
print(f'Functions: {api_flow.Config.function_path}', file=sys.stderr)
print(f' Profiles: {api_flow.Config.profile_path}', file=sys.stderr)
print(f'Templates: {api_flow.Config.template_path}', file=sys.stderr)

if args.profile:
    print('PROFILES:', file=sys.stderr)
    for profile in args.profile:
        print(f' - {os.path.join(api_flow.Config.profile_path, profile)}.yaml', file=sys.stderr)

print(f'FLOW:\n {os.path.join(api_flow.Config.flow_path, args.flow_name)}.yaml', file=sys.stderr)

api_flow.execute(args.flow_name, profiles=args.profile)
