Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.minutesolicitation.MinuteSolicitationWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'generateorder', '-', 'search', '->', 'download'],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    { header: 'Número do Pedido', dataIndex: 'number', width: 120 },
                    { header: 'Ata', dataIndex: 'minute_unicode', width: 60 },
                    { header: 'Edoc', dataIndex: 'edoc_display', id: 'autoExpandColumn' },
                    { header: 'Situação', dataIndex: 'situation_display', width: 120 },
                    { header: 'Descricao', dataIndex: 'unicode', hidden: true },
                    { header: 'Justificativa', dataIndex: 'justification', width: 90, hidden: true },
                    { header: 'modified by', dataIndex: 'modified_by_unicode', width: 120, hidden: true },
                    { header: 'created by', dataIndex: 'created_by_unicode', width: 120, hidden: true },
                    { header: 'created at', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                    { header: 'modified at', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
                ]
            );

        return this._columnModel;
    },

    generateEdoc: function(id) {
        var rest = Ext._create('planning.hiring.minutesolicitationrequisition.MinuteSolicitationRequisitionRestful');
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Gerando Edoc...' });

        mask.show();
        rest.rendererEdoc(
            id,
            {
                scope: this,
                fn: function(message) {
                    var _window = Ext._create(
                        'planning.hiring.minutesolicitationmanager.EdocTextWindow'
                    );

                    // Refactoring
                    _window.insertText(message);

                    _window.oId = id;

                    _window.show();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Gerando Edoc',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    mask.hide();
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getGenerateorderAction: function () {
        if (!this._generateOrder)  {
            this._generateOrder = Ext._create('Ext.Button', {
                text: 'Gerar Pedido',
                iconCls: 'icon-agree icon-agree-appointment-new',
                scope: this,
                handler: function () {
                    var selected = this.getSelectionModel().getSelected();

                    if(selected) {
                        this.generateEdoc(selected.id);
                    }
                    else {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Primeiro selecione um pedido.'
                        });
                    }
                }
            });
        }
        return this._generateOrder;
    },
});

core.RestfulGrid.register(
    'planning.hiring.minutesolicitation.MinuteSolicitationRestful',
    'planning.hiring.minutesolicitation.MinuteSolicitationGrid'
);