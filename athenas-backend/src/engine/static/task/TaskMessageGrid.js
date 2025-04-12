/**
 *
 **/
Ext._define('engine.TaskMessageGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'engine.TaskMessageWindow',

    hideActions: ['add', 'edit', 'delete'],

    rendererDownloadIcon: function(value){
        var tpl = new Ext.XTemplate('<div class="tk-grid-icon-cell {iconCls}" ext:qtip="{title}" <tpl if="width">ext:qwidth="{width}</tpl>"></div>');
        var out = '';

        Ext.each(value, function(item) {
            if(item)
                out += tpl.apply({
                    'iconCls': 'icon-core icon-core-attachment',
                    'title': 'download',
                    'width': (item.width ? item.width : false)
                });
        });

        return out;
    },

    getConfigCustomActions: function(){
        // engine.TaskMessageGrid.superclass.getConfigActions.call(this);
        if(!this._configCustomActions){
            this._configCustomActions = [];
            this._configCustomActions.push(
                {
                    // iconCls: 'icon-16px icon-core icon-core-attachment',
                    tooltip: 'Download item.',
                    handler: function(action, index) {
                        // try{
                        //     Ext.destroy(Ext.get('downloadIframe'));
                        // }catch(e){
                        //     console.debug('Sem iframe...');
                        // }
                        // Ext.DomHelper.append(document.body, {
                        //     tag: 'iframe',
                        //     id: 'downloadIframeAction',
                        //     frameBorder: 0,
                        //     width: 0,
                        //     height: 0,
                        //     css: 'display:none;visibility:hidden;height:0px',
                        //     src: action._store.data.items[index].data.file_ged_permalink
                        // });
                        toolkit.util.downloadFromURL(action._store.data.items[index].data.file_ged_permalink, 'downloadIframeAction');
                    },
                    getClass: function(value, metaData, record, rowIndex, colIndex, store) {
                        if(record.data.file_ged_permalink != '')
                            return 'icon-16px icon-core icon-core-attachment';
                        else
                            return '';
                    }                    
                }
            );
        }
        return this._configCustomActions;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},              
                    {header: 'Task', dataIndex: 'session_unicode', width: 200},
                    {header: '', dataIndex: 'icons', width:30, renderer: toolkit.util.rendererIconGrid},
                    {header: 'Message', dataIndex: 'message', id: 'autoExpandColumn'},
                    // {header: '', dataIndex: 'file_ged_permalink', width:30, renderer: toolkit.util.rendererIconGrid},
                ]
            );

        return this._columnModel;
    },

    toggleTypeOf: function(tipo) {
        if(!this._filterTypeOf)
            this._filterTypeOf = [1, 2, 3, 4];

        if(this._filterTypeOf.indexOf(tipo) >= 0)
            this._filterTypeOf.remove(tipo);
        else
            this._filterTypeOf.push(tipo);

        this.setFilterProperty('type_of__in', this._filterTypeOf, 1000);
    },

    getFilterMenu: function(){
        return [
            {
                text: 'Por Tipo',
                menu: [
                    {
                        text: 'Informação',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleTypeOf(1); }
                    },{
                        text: 'Cuidado',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleTypeOf(2); }
                    },{
                        text: 'Erro',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleTypeOf(3); }
                    },{
                        text: 'Arquivos',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function() { this.toggleTypeOf(4); }
                    },
                ]
            },
        ]
    },
});

core.RestfulGrid.register(
    'engine.TaskMessageRestful',
    'engine.TaskMessageGrid'
);