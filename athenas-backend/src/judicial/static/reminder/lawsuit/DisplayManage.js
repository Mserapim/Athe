
Ext._define('judicial.reminder.lawsuit.DisplayManage', {
    extend: 'judicial.reminder.DisplayManage',

    windowClass: 'judicial.reminder.lawsuit.Window',
    windowManageClass: 'judicial.reminder.lawsuit.WindowManage',

    defaultParams: function() {
        return {
            lawsuit: this.lawsuitId
        };
    },

    refresh: function() {
        var rest = Ext._create('judicial.reminder.lawsuit.Restful');

        rest.doRequest(
            rest.getRoute('read', false, 'GET', {
                params: {
                    filter: Ext.encode([
                        { property: 'lawsuit', value: this.lawsuitId, stage: 1 },
                        { property: 'deactivated_by__isnull', value: true, stage: 2 }
                    ]),
                    start: 0,
                    limit: 30
                },
                scope: this,
                success: function(xhr) {
                    var result = Ext.decode(xhr.responseText);
                    result.success && this.refreshView(result.collection, result.count);
                }
            })
        );
    },

    start: function() {
        if (!this.lawsuitId) {
            console.error('Não foi informado o lawsuitId não posso continuar');
        } else {
            judicial.reminder.lawsuit.DisplayManage.superclass.start.call(this);
        }
    },

    registerObserver: function() {
        console.log('not implemented registerObserver method')
    },

    unRegisterObserver: function() {
        console.log('not implemented unRegisterObserver method')
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            lawsuitId: null
        });

        judicial.reminder.lawsuit.DisplayManage.superclass.constructor.call(this, cfg);
    }
});
