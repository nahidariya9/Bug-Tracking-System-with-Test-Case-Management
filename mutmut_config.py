def pre_mutation(context):
    # Skip test files and non-route files
    if "test_" in context.filename:
        context.skip = True
    if "templates" in context.filename:
        context.skip = True