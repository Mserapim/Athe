Ext._define('web.intranet.Tree', {
    extend: 'core.RestfulTree',

    restWindow: 'web.intranet.Window',

    folderIndexField: 'parent',

    getFilter: function() {
        return [{
            property: 'kind_of_content',
            value: this.kind_of_content() ? this.kind_of_content() : 0,
            level: 0
        }]
    },
});
