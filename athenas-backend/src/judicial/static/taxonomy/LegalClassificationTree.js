/**
 *
 **/
Ext._define('judicial.taxonomy.LegalClassificationTree', {
    extend: 'core.RestfulTree',

    folderIndexField: 'father',

    taxonomy: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._taxonomy = value;

            !prevent && this.observeTaxonomy();
        }

        return this._taxonomy;
    },

    getFilter: function() {
        return [{
            property: 'version',
            value: this.taxonomy() ? this.taxonomy() : 0,
            level: 0
        }]
    },

    getLoader: function() {
        if(!this._loader) {
            this._loader = Ext._create('Ext.tree.TreeLoader', {
                nodeParameter: 'node',
                url: this.factoryRestful().getRoute('folder').url,
                requestMethod: 'GET',
                baseParams: {
                    filter: Ext.encode(this.getFilter())
                }
            });
        }

        return this._loader;
    },

    observeTaxonomy: function() {
        var root = this.getRootNode();

        this.setParam('version', this.taxonomy());
        this.getRootNode().removeAll();
        this._loader = null;
        root.loader = this.getLoader();

        if(this.taxonomy())
            root.reload();
    }
});
