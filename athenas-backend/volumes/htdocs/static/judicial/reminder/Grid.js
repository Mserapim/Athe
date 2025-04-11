
Ext._define('judicial.reminder.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.reminder.Window',

    configOrderToolBar: ['add', '-' , 'deactivate' ,'-' , 'search', '->'],

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Mostrar desativados',
                    hideOnClick: false,
                    checked: false,
                    listeners: {
                        scope: this,
                        checkchange: this.filterDeactivateds
                    }
                }
            ];

        return this._filterMenu;
    },

    filterDeactivateds: function(item, checked) {
        if(checked)
            this.removeFilterProperty('deactivated_by__isnull', 101);
        else
            this.setFilterProperty('deactivated_by__isnull', true, 101);
    },

    _doDeactivate: function(pkset){
        var rest = Ext._create('judicial.reminder.Restful');
        var mask = new Ext.LoadMask(tile.getEl(), {msg: 'desativando lembrete...'});

        mask.show();
        rest.deactivate(
            pkset,
            {
                scope: this,
                fn: function(rst) {
                    Ext.Msg.show({
                        title: 'Desativar Lembrete',
                        msg: rst.message,
                        icon: rst.success? Ext.Msg.INFO : Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    this.fireEvent('deactivatedItem');
                    this.getStore().load();
                }
            },
            {
                scope: this,
                fn: function() {
                    Ext.Msg.show({
                        title: 'Desativar Lembrete',
                        msg: 'Recurso indisponivel no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() { mask.hide() }
            }

        );
    },

    deactivate: function() {
        var selected = this.getSelectionModel().getSelections();

        if(selected.length > 0) {
            Ext.Msg.show({
                title: 'Desativar Lembrete',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja desativar os itens selecionados?',
                scope: this,
                fn: function(btn) {
                    if(btn === 'yes')
                        this._doDeactivate(
                            selected.map(function(data) {
                                return data.get('pk');
                            })
                        );
                }
            });
        }
        else
            Ext.Msg.show({
                title: 'Desativar Lembrete',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione os lembretes que deseja desativar.'
            });
    },

    getDeactivateAction: function(cfg) {
        if(!this._deactivateAction)
            this._deactivateAction = Ext._create('Ext.Button', {
                text: 'Desativar Lembrete',
                iconCls: 'icon-judicial icon-ejud-noticia-de-fato',
                scope: this,
                handler: this.deactivate
            });

        return this._deactivateAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cod', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                    {header: 'Prioridade', dataIndex: 'reminder_state_display', width: 100},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 150},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, hidden: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
                    {header: 'reminder type', dataIndex: 'reminder_type', width: 90, hidden: true},
                    {header: 'content', dataIndex: 'content', width: 90, hidden: true},
                    {header: 'Destaivado por', dataIndex: 'deactived_by_unicode', width: 120, hidden: true},
                    {header: 'Lotação', dataIndex: 'workplace_unicode', width: 120, hidden: true}
                ]
            );

        return this._columnModel;
    },
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                viewConfig: {
                    getRowClass: function(record, rowIndex, rp, ds){
                        var classes = ['grid-line-height-150'];

                        if(!record.get('is_active'))
                            classes.push('x-grid3-dashed');

                        if(record.data.reminder_state == 1)
                            classes.push('x-grid3-red-simple');
                        else if(record.data.reminder_state == 2)
                            classes.push('x-grid3-yellow-simple');
                        else if(record.data.reminder_state == 3)
                            classes.push('x-grid3-green-simple');

                        return classes.join(' ');
                    }
                }
            }
        );

        judicial.reminder.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'judicial.reminder.Restful',
    'judicial.reminder.Grid'
);
